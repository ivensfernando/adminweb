// src/pages/Dashboard.tsx
import { useAuthenticated, useGetIdentity } from 'react-admin';

const Dashboard = () => {
    useAuthenticated();
    const { data: identity } = useGetIdentity();

    return (
        <div style={{ padding: 30 }}>
            <h1>Welcome, {identity?.fullName || 'Trader'}!</h1>
            <p>This is your dashboard.</p>
        </div>
    );
};

export default Dashboard;
