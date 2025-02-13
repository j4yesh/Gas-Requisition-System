import React, { useState, useEffect } from 'react';
const API_URL = process.env.REACT_APP_API_URL;

console.log(API_URL);

// Auth Context
const AuthContext = React.createContext(null);
const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};

// Auth Provider Component
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem('user');
    return storedUser ? JSON.parse(storedUser) : null; // Parse user from localStorage
  });
  const [token, setToken] = useState(localStorage.getItem('token'));

  const login = (userData, authToken) => {
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('token', authToken);
    localStorage.setItem('user', JSON.stringify(userData)); // Store user as JSON string
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const CreateRequest = ({ onNavigate }) => {
  const [formData, setFormData] = useState({
    type: '',
    detail: '',
  });
  const [error, setError] = useState('');
  const { token } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/request/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      console.log(response);

      if (!response.ok) throw new Error('Failed to submit request');

      onNavigate('dashboard');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold">Create New Request</h1>
            <button
              onClick={() => onNavigate('dashboard')}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-4 py-6">
        {error && <div className="text-red-500 mb-4">{error}</div>}

        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow">
          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">Request Type</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              className="w-full px-4 py-2 border rounded"
              required
            >
              <option value="">Select Request Type</option>
              <option value="Gas A">Gas A</option>
              <option value="Gas B">Gas B</option>
              <option value="Gas C">Gas C</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">Details</label>
            <textarea
              value={formData.detail}
              onChange={(e) => setFormData({ ...formData, detail: e.target.value })}
              className="w-full px-4 py-2 border rounded"
              rows="4"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Submit Request
          </button>
        </form>
      </main>
    </div>
  );
};

const AppContainer = () => {
  const [currentPage, setCurrentPage] = useState('login');
  const { token, user } = useAuth();

  useEffect(() => {
    if (token && currentPage === 'login') {
      setCurrentPage('dashboard');
    } else if (!token && currentPage === 'dashboard') {
      setCurrentPage('login');
    }
  }, [token, currentPage]);

  const renderPage = () => {
    switch (currentPage) {
      case 'login':
        return <Login onNavigate={setCurrentPage} />;
      case 'register':
        return <Register onNavigate={setCurrentPage} />;
      case 'dashboard':
        return <Dashboard onNavigate={setCurrentPage} />;
      case 'create-request':
        return <CreateRequest onNavigate={setCurrentPage} />;
      default:
        return <Login onNavigate={setCurrentPage} />;
    }
  };

  return renderPage();
};

// Root App Component
const App = () => {
  return (
    <AuthProvider>
      <AppContainer />
    </AuthProvider>
  );
};

// Login Component
const Login = ({ onNavigate }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      console.log(username);

      if (response.ok) {
        const { role, access } = data; // Extract role from API response
        login({ username, role }, access); // Store role along with username
        onNavigate('dashboard');
        console.log('Switching to dashboard');
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to login');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Login</h2>
        {error && <div className="text-red-500 text-center">{error}</div>}
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              className="w-full px-4 py-2 border rounded"
            />
          </div>
          <div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full px-4 py-2 border rounded"
            />
          </div>
          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Login
          </button>
        </form>
        <div className="text-center mt-4">
          <button
            onClick={() => onNavigate('register')}
            className="text-blue-500 hover:text-blue-600"
          >
            Register new account
          </button>
        </div>
      </div>
    </div>
  );
};

// Register Component
const Register = ({ onNavigate }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    role: 'customer',
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(formData);
    try {
      const response = await fetch(`${API_URL}/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await response.json();

      if (response.ok) {
        onNavigate('login');
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to register');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Register</h2>
        {error && <div className="text-red-500 text-center">{error}</div>}
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          <div>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              placeholder="Username"
              className="w-full px-4 py-2 border rounded"
            />
          </div>
          <div>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Password"
              className="w-full px-4 py-2 border rounded"
            />
          </div>
          <div>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              className="w-full px-4 py-2 border rounded"
            >
              <option value="customer">Customer</option>
              <option value="servitor">Servitor</option>
            </select>
          </div>
          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Register
          </button>
        </form>
        <div className="text-center mt-4">
          <button
            onClick={() => onNavigate('login')}
            className="text-blue-500 hover:text-blue-600"
          >
            Already have an account? Login
          </button>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = ({ onNavigate }) => {
  const { user, token, logout } = useAuth();
  const [requisitions, setRequisitions] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRequisitions = async () => {
      try {
        console.log('Fetching the data');
        console.log('role: ' + user?.role);
        const endpoint =
          user?.role === 'servitor'
            ? `${API_URL}/servitor/request`
            : `${API_URL}/request/get`;

        const response = await fetch(endpoint, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) throw new Error('Failed to fetch requisitions');

        const data = await response.json();
        console.log('Fetched data', data);
        console.log(user);
        setRequisitions(data.requisitions);
      } catch (err) {
        setError('Failed to load requisitions');
      }
    };

    fetchRequisitions();
  }, [token, user]);

  const handleLogout = () => {
    logout();
    onNavigate('login');
  };

  const handleSelfAppoint = async (reqId) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      alert('Authorization token is missing');
      return;
    }

    const response = await fetch(`${API_URL}/servitor/selfappoint/${reqId}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) throw new Error('Failed to self-appoint');

    alert('You have been assigned to this request');
    window.location.reload();

  } catch (error) {
    console.error('Error appointing self:', error);
    alert('Failed to appoint yourself');
  }
};


  const handleStatusChange = async (reqId, idx) => {
    try {
      const token = localStorage.getItem('token'); // Assuming token is stored in localStorage
      if (!token) {
        alert('Authorization token is missing');
        return;
      }

      const response = await fetch(`${API_URL}/servitor/status/${reqId}/${idx}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error('Failed to update status');
      }

      alert('Status updated successfully');

      // You may want to refresh data after update
      window.location.reload();

    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update status');
    }
  };

  // Separate requests into two lists (for servitors)
  const myRequests = requisitions.filter((req) => req.servitor === user?.username);
  const otherRequests = requisitions.filter((req) => req.servitor !== user?.username);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold">Gas Requisition System</h1>
            <p className="text-1sm font-bold align-top">
  <span className="text-1sm font-bold block">Bynry Services Backend Developer Intern Case study</span>
  Applicant Name: Jayesh Badgujar
</p>

            

            <div className="flex items-center space-x-4">
              {user?.role === 'customer' && (
                <button
                  onClick={() => onNavigate('create-request')}
                  className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  Create New Request
                </button>
              )}
              <span>Welcome, {user?.username}</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {error && <div className="text-red-500 mb-4">{error}</div>}

        {user?.role === 'servitor' ? (
          <div className="flex space-x-6">
            {/* Requests Assigned to Other Servitors */}
            <div className="w-1/2 h-[500px] overflow-y-auto bg-gray-100 p-4 rounded-lg">
              <h2 className="text-lg font-semibold mb-4">Other Requests</h2>
              <div className="space-y-4">
                {otherRequests.map((req, index) => (
                  
                  <div key={index} className="bg-white p-3 rounded-lg shadow">
    <h3 className="text-md font-semibold">Request Type: {req.type}</h3>
    <p className="text-sm text-gray-600">Servitor: {req.servitor || 'Not Assigned'}</p>
    <p className="text-sm text-gray-600">Customer: {req.username}</p>
    <p className="mt-1 text-sm">{req.detail}</p>

    {/* Self Appoint Button */}
    {(!req.servitor || req.servitor === 'To be appointed') && (
      <button
        onClick={() => handleSelfAppoint(req._id)}
        className="mt-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Self Appoint
      </button>
    )}

    <div className="mt-2">
      <h4 className="font-medium text-sm mb-1">Progress:</h4>
      <div className="space-y-1">
        {req.status.map((status, idx) => (
          <div
            key={idx}
            className={`p-1 rounded ${status.completed ? 'bg-green-100' : 'bg-gray-100'}`}
          >
            <span className={status.completed ? 'text-green-600' : 'text-gray-600'}>
              {status.stage}
            </span>
            {status.timestamp && (
              <span className="text-xs text-gray-500 ml-1">
                {new Date(status.timestamp).toLocaleString()}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  </div>

                ))}
              </div>
            </div>

            {/* Requests Assigned to Current Servitor */}
            <div className="w-1/2 h-[500px] overflow-y-auto bg-gray-100 p-4 rounded-lg">
              <h2 className="text-lg font-semibold mb-4">My Assigned Requests</h2>
              <div className="space-y-4">
                {myRequests.map((req, index) => (
                  <div key={index} className="bg-white p-2 rounded-lg shadow">
                    <h3 className="text-md font-semibold">Request Type: {req.type}</h3>
                    <p className="text-sm text-gray-600">Servitor: {req.servitor}</p>
                    <p className="text-sm text-gray-600">Customer: {req.username}</p>
                    <p className="mt-1 text-sm">{req.detail}</p>
                    <div className="mt-2">
                      <h4 className="font-medium text-sm mb-1">Progress:</h4>
                      <div className="space-y-1">
                        {req.status.map((status, idx) => (
                          <div
                            key={idx}
                            className={`p-1 rounded flex items-center gap-2 ${
                              status.completed ? 'bg-green-100' : 'bg-gray-100'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={status.completed}
                              onChange={() => handleStatusChange(req._id, idx)}
                              disabled={status.completed} // Prevent re-updating
                              className="cursor-pointer"
                            />
                            <span
                              className={status.completed ? 'text-green-600' : 'text-gray-600'}
                            >
                              {status.stage}
                            </span>
                            {status.timestamp && (
                              <span className="text-xs text-gray-500 ml-1">
                                {new Date(status.timestamp).toLocaleString()}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          // Default display for non-servitors
          <div className="grid gap-6">
            {requisitions.map((req, index) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-md font-semibold">Request Type: {req.type}</h3>
                <p className="text-sm text-gray-600">Servitor: {req.servitor}</p>
                <p className="text-sm text-gray-600">Customer: {req.username}</p>
                <p className="mt-1 text-sm">{req.detail}</p>
                <div className="mt-2">
                  <h4 className="font-medium text-sm mb-1">Progress:</h4>
                  <div className="space-y-1">
                    {req.status.map((status, idx) => (
                      <div
                        key={idx}
                        className={`p-1 rounded ${
                          status.completed ? 'bg-green-100' : 'bg-gray-100'
                        }`}
                      >
                        <span className={status.completed ? 'text-green-600' : 'text-gray-600'}>
                          {status.stage}
                        </span>
                        {status.timestamp && (
                          <span className="text-xs text-gray-500 ml-1">
                            {new Date(status.timestamp).toLocaleString()}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default App;