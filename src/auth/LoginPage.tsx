import { useLogin, useNotify, useRedirect } from 'react-admin';
import { useState } from 'react';

const LoginPage = () => {
    const login = useLogin();
    const notify = useNotify();
    const redirect = useRedirect();

    const [form, setForm] = useState({ username: '', password: '' });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await login(form);
            redirect('/');
        } catch {
            notify('Invalid credentials');
        }
    };

    return (
        <div style={{ margin: '100px auto', width: 300 }}>
            <h2>Login</h2>
            <form onSubmit={handleSubmit}>
                <input name="username" placeholder="Username" value={form.username}
                       onChange={(e) => setForm({ ...form, username: e.target.value })} />
                <input name="password" type="password" placeholder="Password" value={form.password}
                       onChange={(e) => setForm({ ...form, password: e.target.value })} />
                <button type="submit" style={{ width: '100%', marginTop: 10 }}>Login</button>
            </form>
            <button onClick={() => redirect('/create-user')} style={{ width: '100%', marginTop: 20 }}>
                Create New User
            </button>
        </div>
    );
};

export default LoginPage;
