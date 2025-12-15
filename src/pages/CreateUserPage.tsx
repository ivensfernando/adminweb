// src/pages/CreateUserPage.tsx
import { useNotify, useRedirect } from 'react-admin';
import { useState } from 'react';
import { API_V1_URL } from '../config/api';
import { Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';

type CreateUserForm = {
    username: string;
    password: string;
    email: string;
    firstName: string;
    lastName: string;
    phoneNumber: string;
    timezone: string;
};

const defaultForm: CreateUserForm = {
    username: '',
    password: '',
    email: '',
    firstName: '',
    lastName: '',
    phoneNumber: '',
    timezone: '',
};

const CreateUserPage = () => {
    const notify = useNotify();
    const redirect = useRedirect();
    const [form, setForm] = useState<CreateUserForm>(defaultForm);
    const [submitting, setSubmitting] = useState(false);

    const handleChange = (field: keyof CreateUserForm) => (event: React.ChangeEvent<HTMLInputElement>) => {
        setForm((prev) => ({ ...prev, [field]: event.target.value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            const res = await fetch(`${API_V1_URL}/auth/register`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form),
            });

            if (res.status === 409) {
                const message =
                    (await res.text()) || 'User already exists. Please choose a different username.';
                notify(message, { type: 'warning' });
                return
            }
            if (!res.ok) {
                const errorMessage = (await res.text()) || 'Failed to create user';
                throw new Error(errorMessage);
            }

            notify('User created successfully');
            redirect('/login');
        } catch (error) {
            console.error('Error creating user', error);
            notify(error instanceof Error ? error.message : 'Failed to create user', { type: 'error' });
        } finally {
            setSubmitting(false);
        }
    };
    // admin java3322321
    // root openSesame

    return (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" px={2}>
            <Card sx={{ maxWidth: 480, width: '100%' }}>
                <CardContent>
                    <Typography variant="h5" component="h2" gutterBottom>
                        Create New User
                    </Typography>
                    <Box component="form" onSubmit={handleSubmit} noValidate>
                        <Stack spacing={2}>
                            <TextField
                                label="Username"
                                name="username"
                                value={form.username}
                                onChange={handleChange('username')}
                                required
                                fullWidth
                            />
                            <TextField
                                label="Password"
                                name="password"
                                type="password"
                                value={form.password}
                                onChange={handleChange('password')}
                                required
                                fullWidth
                            />
                            <TextField
                                label="Email"
                                name="email"
                                type="email"
                                value={form.email}
                                onChange={handleChange('email')}
                                required
                                fullWidth
                            />
                            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                                <TextField
                                    label="First Name"
                                    name="firstName"
                                    value={form.firstName}
                                    onChange={handleChange('firstName')}
                                    fullWidth
                                />
                                <TextField
                                    label="Last Name"
                                    name="lastName"
                                    value={form.lastName}
                                    onChange={handleChange('lastName')}
                                    fullWidth
                                />
                            </Stack>
                            <TextField
                                label="Phone Number"
                                name="phoneNumber"
                                value={form.phoneNumber}
                                onChange={handleChange('phoneNumber')}
                                fullWidth
                            />
                            <TextField
                                label="Timezone"
                                name="timezone"
                                placeholder="e.g. America/New_York"
                                value={form.timezone}
                                onChange={handleChange('timezone')}
                                fullWidth
                            />
                            <Button type="submit" variant="contained" color="primary" disabled={submitting}>
                                {submitting ? 'Creating...' : 'Create Account'}
                            </Button>
                        </Stack>
                    </Box>
                </CardContent>
            </Card>
        </Box>
    );
};

export default CreateUserPage;
