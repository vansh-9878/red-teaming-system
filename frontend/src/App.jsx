import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import AnalyticsView from './components/AnalyticsView';
import ProbeInspector from './components/ProbeInspector';
import PatchGeneratorView from './components/PatchGeneratorView';
import ModelConfigModal from './components/ModelConfigModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [mode, setMode] = useState('coordinator'); // 'coordinator' | 'single'
  const [selectedAgent, setSelectedAgent] = useState('persona');
  const [totalRounds, setTotalRounds] = useState(15);
  const [objectiveMode, setObjectiveMode] = useState('autonomous');
  const [customGoal, setCustomGoal] = useState('');
  
  const [isRunning, setIsRunning] = useState(false);
  const [currentStatus, setCurrentStatus] = useState('');
  const [messages, setMessages] = useState([]);
  const [banditState, setBanditState] = useState(null);
  const [campaignSummary, setCampaignSummary] = useState(null);
  const [isModelConfigOpen, setIsModelConfigOpen] = useState(false);

  const [modelsInfo, setModelsInfo] = useState({
    target: 'smollm2:1.7b (OLLAMA)',
    attacker: 'qwen/qwen3.6-27b (GROQ)',
    judge: 'openai/gpt-oss-20b (GROQ)',
    patcher: 'qwen/qwen3.6-27b (GROQ)'
  });

  const wsRef = useRef(null);

  const refreshModelsConfig = () => {
    fetch('http://localhost:8000/config/models')
      .then(res => res.json())
      .then(data => {
        if (data.target_chatbot) {
          setModelsInfo({
            target: `${data.target_chatbot.model} (${data.target_chatbot.provider.toUpperCase()})`,
            attacker: `${data.attacker_agents.model} (${data.attacker_agents.provider.toUpperCase()})`,
            judge: `${data.judge_scorer.model} (${data.judge_scorer.provider.toUpperCase()})`,
            patcher: data.patch_generator ? `${data.patch_generator.model} (${data.patch_generator.provider.toUpperCase()})` : 'qwen/qwen3.6-27b (GROQ)'
          });
        }
      })
      .catch(() => {});
  };

  // Fetch initial model config and bandit state from backend
  useEffect(() => {
    refreshModelsConfig();

    fetch('http://localhost:8000/coordinator/state')
      .then(res => res.json())
      .then(data => {
        setBanditState(data);
      })
      .catch(() => {});
  }, []);

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/coordinator/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[WebSocket] Connected to SentinelLoop backend.');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'campaign_started':
          setIsRunning(true);
          setCurrentStatus('Campaign initialized. Selecting first specialist...');
          setCampaignSummary(null);
          break;

        case 'round_start':
          setCurrentStatus(`Round ${data.round}/${data.total_rounds}: Scheduling ${data.agent_name}...`);
          break;

        case 'attacker_thinking':
          setCurrentStatus(`⚔️ ${data.agent_name} is generating adversarial probe...`);
          break;

        case 'probe_generated':
          setCurrentStatus(`⚔️ Probe generated (${data.strategy_used}). Forwarding to target...`);
          setMessages(prev => {
            const existingIdx = prev.findIndex(m => m.round === data.round);
            if (existingIdx >= 0) {
              const updated = [...prev];
              updated[existingIdx] = { ...updated[existingIdx], ...data };
              return updated;
            } else {
              return [...prev, data];
            }
          });
          break;

        case 'target_thinking':
          setCurrentStatus(`🎯 Target model (${data.target_model || 'Chatbot'}) is responding...`);
          break;

        case 'target_replied':
          setCurrentStatus(`🎯 Target reply received. Sentinel Judge evaluating...`);
          setMessages(prev => {
            const existingIdx = prev.findIndex(m => m.round === data.round);
            if (existingIdx >= 0) {
              const updated = [...prev];
              updated[existingIdx] = { ...updated[existingIdx], response: data.response };
              return updated;
            }
            return prev;
          });
          break;

        case 'evaluating':
          setCurrentStatus(`⚖️ Sentinel Judge scoring interaction & detecting leaks...`);
          break;

        case 'round_completed':
          setCurrentStatus('');
          setMessages(prev => {
            const existingIdx = prev.findIndex(m => m.round === data.round);
            if (existingIdx >= 0) {
              const updated = [...prev];
              updated[existingIdx] = { ...updated[existingIdx], ...data };
              return updated;
            } else {
              return [...prev, data];
            }
          });
          if (data.bandit_state) {
            setBanditState(data.bandit_state);
          }
          break;

        case 'patch_auto_applied':
          setCurrentStatus(`🛡️ Live Patch Auto-Applied: [${data.patch?.patch_type || 'defense'}] in round ${data.round}!`);
          setMessages(prev => {
            const existingIdx = prev.findIndex(m => m.round === data.round);
            if (existingIdx >= 0) {
              const updated = [...prev];
              updated[existingIdx] = { ...updated[existingIdx], auto_patch: data.patch };
              return updated;
            }
            return prev;
          });
          break;

        case 'campaign_completed':
          setIsRunning(false);
          setCurrentStatus('');
          setCampaignSummary(data);
          break;

        case 'reset_completed':
          setMessages([]);
          setCampaignSummary(null);
          if (data.bandit_state) {
            setBanditState(data.bandit_state);
          }
          break;

        case 'error':
          console.error('[WebSocket error]:', data.message);
          setCurrentStatus('');
          setIsRunning(false);
          break;

        default:
          break;
      }
    };

    ws.onclose = () => {
      console.log('[WebSocket] Connection closed.');
      setIsRunning(false);
      setCurrentStatus('');
    };

    return ws;
  };

  const handleStartCampaign = () => {
    setMessages([]);
    setCampaignSummary(null);
    setActiveTab('chat');

    let ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      ws = connectWebSocket();
      ws.onopen = () => {
        sendStartPayload(ws);
      };
    } else {
      sendStartPayload(ws);
    }
  };

  const sendStartPayload = (ws) => {
    const payload = {
      action: 'start',
      mode: mode,
      total_rounds: totalRounds,
      goal: objectiveMode === 'custom' && customGoal.trim() ? customGoal.trim() : null,
      agent: selectedAgent
    };
    ws.send(JSON.stringify(payload));
  };

  const handleStopCampaign = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
    setIsRunning(false);
    setCurrentStatus('');
  };

  const handleReset = () => {
    setMessages([]);
    setCampaignSummary(null);
    fetch('http://localhost:8000/coordinator/reset', { method: 'POST' })
      .then(res => res.json())
      .then(() => {
        return fetch('http://localhost:8000/coordinator/state');
      })
      .then(res => res.json())
      .then(data => setBanditState(data))
      .catch(() => {});
  };

  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      width: '100vw',
      backgroundColor: '#000000',
      overflow: 'hidden'
    }}>
      {/* Left Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        mode={mode}
        setMode={setMode}
        selectedAgent={selectedAgent}
        setSelectedAgent={setSelectedAgent}
        totalRounds={totalRounds}
        setTotalRounds={setTotalRounds}
        objectiveMode={objectiveMode}
        setObjectiveMode={setObjectiveMode}
        customGoal={customGoal}
        setCustomGoal={setCustomGoal}
        isRunning={isRunning}
        onStartCampaign={handleStartCampaign}
        onStopCampaign={handleStopCampaign}
        onReset={handleReset}
        modelsInfo={modelsInfo}
        onOpenModelConfig={() => setIsModelConfigOpen(true)}
      />

      {/* Main View Area */}
      {activeTab === 'chat' && (
        <ChatInterface
          messages={messages}
          currentStatus={currentStatus}
          targetModel={modelsInfo.target}
        />
      )}

      {activeTab === 'analytics' && (
        <AnalyticsView
          banditState={banditState}
          campaignSummary={campaignSummary}
          totalRounds={totalRounds}
        />
      )}

      {activeTab === 'inspector' && (
        <ProbeInspector
          messages={messages}
        />
      )}

      {activeTab === 'patcher' && (
        <PatchGeneratorView
          messages={messages}
          campaignSummary={campaignSummary}
        />
      )}

      {/* Model & API Key Configuration Modal */}
      <ModelConfigModal
        isOpen={isModelConfigOpen}
        onClose={() => setIsModelConfigOpen(false)}
        onSaveSuccess={refreshModelsConfig}
      />
    </div>
  );
}
