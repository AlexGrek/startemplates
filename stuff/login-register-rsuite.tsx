import React, { useState, useEffect } from 'react';
import { Panel, Form, Input, Button, ButtonToolbar, Loader, Message, useToaster, Nav } from 'rsuite';
import { User, Lock } from 'lucide-react';

const API_BASE = '/api/v1';

function LoginRegisterPage() {
  const [activeTab, setActiveTab] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const toaster = useToaster();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/whoami`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.username) {
          window.location.href = '/home';
          return;
        }
      }
    } catch (err) {
      // User not authenticated, continue to login page
    } finally {
      setCheckingAuth(false);
    }
  };

  const handleSubmit = async () => {
    if (!username || !password) {
      toaster.push(
        <Message showIcon type="warning">
          Please fill in all fields
        </Message>,
        { placement: 'topCenter', duration: 3000 }
      );
      return;
    }

    setLoading(true);
    const endpoint = activeTab === 'login' ? '/auth/login' : '/auth/register';
    
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });

      if (response.ok || response.status === 201) {
        toaster.push(
          <Message showIcon type="success">
            {activeTab === 'login' ? 'Login successful!' : 'Registration successful!'}
          </Message>,
          { placement: 'topCenter', duration: 2000 }
        );
        setTimeout(() => {
          window.location.href = '/home';
        }, 500);
      } else {
        const data = await response.json().catch(() => ({}));
        const errorMsg = data.detail || data.message || `${activeTab === 'login' ? 'Login' : 'Registration'} failed`;
        toaster.push(
          <Message showIcon type="error">
            {errorMsg}
          </Message>,
          { placement: 'topCenter', duration: 4000 }
        );
      }
    } catch (err) {
      toaster.push(
        <Message showIcon type="error">
          Network error. Please try again.
        </Message>,
        { placement: 'topCenter', duration: 4000 }
      );
    } finally {
      setLoading(false);
    }
  };

  if (checkingAuth) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Loader size="lg" content="Loading..." />
      </div>
    );
  }

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{ width: '100%', maxWidth: '450px' }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h2>Welcome</h2>
          <p>Sign in to continue to your account</p>
        </div>

        <Panel bordered>
          <Nav 
            appearance="tabs" 
            activeKey={activeTab} 
            onSelect={setActiveTab}
            style={{ marginBottom: '20px' }}
          >
            <Nav.Item eventKey="login">Login</Nav.Item>
            <Nav.Item eventKey="register">Register</Nav.Item>
          </Nav>

          <Form fluid>
            <Form.Group>
              <Form.ControlLabel>
                <User size={16} style={{ marginRight: '5px', verticalAlign: 'middle' }} />
                Username
              </Form.ControlLabel>
              <Input 
                value={username}
                onChange={setUsername}
                placeholder="Enter your username"
                disabled={loading}
                onPressEnter={handleSubmit}
              />
            </Form.Group>

            <Form.Group>
              <Form.ControlLabel>
                <Lock size={16} style={{ marginRight: '5px', verticalAlign: 'middle' }} />
                Password
              </Form.ControlLabel>
              <Input 
                type="password"
                value={password}
                onChange={setPassword}
                placeholder="Enter your password"
                disabled={loading}
                onPressEnter={handleSubmit}
              />
            </Form.Group>

            <Form.Group>
              <ButtonToolbar>
                <Button 
                  appearance="primary" 
                  onClick={handleSubmit}
                  loading={loading}
                  block
                >
                  {activeTab === 'login' ? 'Login' : 'Register'}
                </Button>
              </ButtonToolbar>
            </Form.Group>
          </Form>
        </Panel>

        <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '12px', color: '#999' }}>
          By continuing, you agree to our Terms of Service
        </div>
      </div>
    </div>
  );
}

export default LoginRegisterPage;