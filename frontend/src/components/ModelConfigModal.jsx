import React, { useState, useEffect } from 'react';
import { 
  X, 
  Settings, 
  Target, 
  Cpu, 
  Scale, 
  Wrench, 
  Check, 
  Key, 
  Server, 
  Sparkles, 
  AlertCircle 
} from 'lucide-react';

export default function ModelConfigModal({ isOpen, onClose, onSaveSuccess }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetch('http://localhost:8000/config/models')
        .then(res => res.json())
        .then(data => {
          setConfig(data);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to load model config:', err);
          setLoading(false);
        });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleFieldChange = (role, field, value) => {
    setConfig(prev => ({
      ...prev,
      [role]: {
        ...prev[role],
        [field]: value
      }
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveStatus(null);
    try {
      const res = await fetch('http://localhost:8000/config/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to save configuration');
      }
      const data = await res.json();
      setSaveStatus({ type: 'success', message: 'Model configuration updated successfully!' });
      if (onSaveSuccess) onSaveSuccess(data);
      setTimeout(() => {
        onClose();
      }, 1200);
    } catch (err) {
      setSaveStatus({ type: 'error', message: err.message });
    } finally {
      setSaving(false);
    }
  };

  const popularModels = {
    gemini: [
      'gemini-2.0-flash-lite',
      'gemini-2.0-flash',
      'gemini-1.5-flash',
      'gemini-1.5-pro'
    ],
    groq: [
      'qwen/qwen3.8-27b',
      'allam-2-7b',
      'openai/gpt-oss-120b',
      'openai/gpt-oss-20b',
      'llama-3.3-70b-versatile',
      'llama-3.1-8b-instant'
    ],
    grok: [
      'grok-2-latest',
      'grok-beta',
      'grok-2-vision-1212'
    ],
    ollama: [
      'smollm2:1.7b',
      'llama3:8b',
      'qwen2.5:7b',
      'mistral:latest',
      'deepseek-r1:8b'
    ]
  };

  const renderRoleSection = (roleKey, title, Icon, color) => {
    const roleData = config ? config[roleKey] || {} : {};
    const provider = roleData.provider || 'gemini';

    return (
      <div style={{
        backgroundColor: '#140D07',
        border: '1px solid #32210F',
        borderRadius: '10px',
        padding: '1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #281A0E', paddingBottom: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <Icon size={16} color={color} />
            <span style={{ fontSize: '0.86rem', fontWeight: 700, color: '#E1DCC9' }}>{title}</span>
          </div>
          <span style={{ fontSize: '0.7rem', color: '#A89E8C', textTransform: 'uppercase', fontFamily: 'monospace' }}>
            {roleKey}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: '0.75rem' }}>
          {/* Provider Selector */}
          <div>
            <label style={{ fontSize: '0.72rem', color: '#A89E8C', fontWeight: 600, display: 'block', marginBottom: '0.25rem' }}>
              Provider
            </label>
            <select
              value={provider}
              onChange={(e) => {
                const newProv = e.target.value;
                handleFieldChange(roleKey, 'provider', newProv);
                if (newProv === 'gemini') {
                  handleFieldChange(roleKey, 'base_url', 'https://generativelanguage.googleapis.com/v1beta/openai');
                  handleFieldChange(roleKey, 'model', 'gemini-2.0-flash-lite');
                } else if (newProv === 'groq') {
                  handleFieldChange(roleKey, 'base_url', 'https://api.groq.com/openai/v1');
                  handleFieldChange(roleKey, 'model', 'qwen/qwen3.8-27b');
                } else if (newProv === 'grok') {
                  handleFieldChange(roleKey, 'base_url', 'https://api.x.ai/v1');
                  handleFieldChange(roleKey, 'model', 'grok-2-latest');
                } else if (newProv === 'ollama') {
                  handleFieldChange(roleKey, 'base_url', 'http://localhost:11434');
                  handleFieldChange(roleKey, 'model', 'smollm2:1.7b');
                }
              }}
              style={{
                width: '100%',
                backgroundColor: '#1F150C',
                border: '1px solid #412D15',
                borderRadius: '6px',
                color: '#E1DCC9',
                padding: '0.45rem 0.6rem',
                fontSize: '0.78rem',
                outline: 'none'
              }}
            >
              <option value="gemini">Google Gemini (Gemini 2.0 / Flash Lite)</option>
              <option value="groq">Groq Cloud (Fast LPU)</option>
              <option value="grok">xAI Grok (Direct)</option>
              <option value="ollama">Ollama (Local Substrate)</option>
            </select>
          </div>

          {/* Model Name Input / Suggestions */}
          <div>
            <label style={{ fontSize: '0.72rem', color: '#A89E8C', fontWeight: 600, display: 'block', marginBottom: '0.25rem' }}>
              Model Name / Identifier
            </label>
            <input
              type="text"
              list={`${roleKey}-model-suggestions`}
              value={roleData.model || ''}
              onChange={(e) => handleFieldChange(roleKey, 'model', e.target.value)}
              placeholder="e.g. gemini-2.0-flash-lite, qwen/qwen3.8-27b"
              style={{
                width: '100%',
                backgroundColor: '#1F150C',
                border: '1px solid #412D15',
                borderRadius: '6px',
                color: '#E1DCC9',
                padding: '0.45rem 0.6rem',
                fontSize: '0.78rem',
                fontFamily: 'monospace',
                outline: 'none'
              }}
            />
            <datalist id={`${roleKey}-model-suggestions`}>
              {(popularModels[provider] || []).map(m => (
                <option key={m} value={m} />
              ))}
            </datalist>
          </div>
        </div>

        {/* API Key (if Gemini, Groq or Grok) */}
        {provider !== 'ollama' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
              <label style={{ fontSize: '0.72rem', color: '#A89E8C', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Key size={12} color="#D97706" />
                {provider === 'gemini' ? 'Google Gemini API Key (AIzaSy...)' : provider === 'groq' ? 'Groq API Key (gsk_...)' : 'xAI Grok API Key (xai-...)'}
              </label>
            </div>
            <input
              type="password"
              value={roleData.api_key || ''}
              onChange={(e) => handleFieldChange(roleKey, 'api_key', e.target.value)}
              placeholder={provider === 'gemini' ? 'Enter Google Gemini API Key...' : provider === 'groq' ? 'Enter Groq API Key...' : 'Enter Grok API Key...'}
              style={{
                width: '100%',
                backgroundColor: '#1F150C',
                border: '1px solid #412D15',
                borderRadius: '6px',
                color: '#E1DCC9',
                padding: '0.45rem 0.6rem',
                fontSize: '0.78rem',
                fontFamily: 'monospace',
                outline: 'none'
              }}
            />
          </div>
        )}

        {/* Custom Base URL (Optional) */}
        <div>
          <label style={{ fontSize: '0.7rem', color: '#736858', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.2rem' }}>
            <Server size={11} /> Base URL Endpoint
          </label>
          <input
            type="text"
            value={roleData.base_url || ''}
            onChange={(e) => handleFieldChange(roleKey, 'base_url', e.target.value)}
            placeholder="http://localhost:11434 or https://api.groq.com/openai/v1"
            style={{
              width: '100%',
              backgroundColor: '#0E0804',
              border: '1px solid #281A0E',
              borderRadius: '6px',
              color: '#A89E8C',
              padding: '0.35rem 0.5rem',
              fontSize: '0.72rem',
              fontFamily: 'monospace',
              outline: 'none'
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.82)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 10000,
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: '#1F150C',
        border: '1px solid #5E4120',
        borderRadius: '16px',
        width: '740px',
        maxWidth: '95vw',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 20px 50px rgba(0,0,0,0.9), 0 0 1px 1px rgba(217, 119, 6, 0.2)'
      }}>
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid #412D15',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              backgroundColor: '#140D07',
              border: '1px solid #412D15',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Settings size={18} color="#D97706" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 800, color: '#E1DCC9', letterSpacing: '-0.01em' }}>
                Model & API Key Configuration
              </h3>
              <p style={{ fontSize: '0.74rem', color: '#A89E8C' }}>
                Configure models and providers for Target, Attacker, Judge, and Adaptive Patch Generator
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              color: '#A89E8C',
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Status Alert */}
        {saveStatus && (
          <div style={{
            margin: '1rem 1.5rem 0',
            padding: '0.65rem 1rem',
            borderRadius: '8px',
            backgroundColor: saveStatus.type === 'success' ? '#2A9D8F22' : '#E6394622',
            border: `1px solid ${saveStatus.type === 'success' ? '#2A9D8F' : '#E63946'}`,
            color: saveStatus.type === 'success' ? '#6EE7B7' : '#FFA5AB',
            fontSize: '0.8rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem'
          }}>
            {saveStatus.type === 'success' ? <Check size={16} /> : <AlertCircle size={16} />}
            <span>{saveStatus.message}</span>
          </div>
        )}

        {/* Body Content */}
        <div style={{
          padding: '1.25rem 1.5rem',
          overflowY: 'auto',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#A89E8C', fontSize: '0.85rem' }}>
              Loading model settings...
            </div>
          ) : (
            <>
              {/* Target Chatbot */}
              {renderRoleSection('target_chatbot', '1. Target Chatbot (System Under Test)', Target, '#D97706')}

              {/* Attacker Agents */}
              {renderRoleSection('attacker_agents', '2. Attacker Squad (Specialist Agents)', Cpu, '#D97706')}

              {/* Judge / Scorer */}
              {renderRoleSection('judge_scorer', '3. Judge / Scorer (Breach Evaluator)', Scale, '#D97706')}

              {/* Adaptive Patch Generator */}
              {renderRoleSection('patch_generator', '4. Adaptive Security Patch Generator (LLM Patcher)', Wrench, '#2A9D8F')}
            </>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid #412D15',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          gap: '0.75rem'
        }}>
          <button
            onClick={onClose}
            style={{
              backgroundColor: 'transparent',
              color: '#A89E8C',
              border: '1px solid #412D15',
              borderRadius: '8px',
              padding: '0.55rem 1rem',
              fontSize: '0.8rem',
              cursor: 'pointer'
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving || loading}
            style={{
              backgroundColor: '#D97706',
              color: '#E1DCC9',
              border: 'none',
              borderRadius: '8px',
              padding: '0.55rem 1.25rem',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: saving || loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              opacity: saving ? 0.7 : 1
            }}
          >
            <Sparkles size={15} />
            {saving ? 'Saving...' : 'Save & Hot-Reload Models'}
          </button>
        </div>
      </div>
    </div>
  );
}
