import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from 'react';
import { Box, Button, Card, CardContent, Stack, TextField, Typography } from '@mui/material';
import { useGetIdentity, useNotify, useRedirect } from 'react-admin';
import { Link as RouterLink } from 'react-router-dom';

import { API_V1_URL } from '../config/api';
import type { UserIdentity } from '../types/user';

type ProfileFormState = {
    username: string;
    email: string;
    firstName: string;
    lastName: string;
    bio: string;
    avatarUrl: string;
};

const emptyForm: ProfileFormState = {
    username: '',
    email: '',
    firstName: '',
    lastName: '',
    bio: '',
    avatarUrl: '',
};

const mapIdentityToForm = (identity?: UserIdentity): ProfileFormState => ({
    username: identity?.username ?? '',
    email: identity?.email ?? '',
    firstName: identity?.firstName ?? '',
    lastName: identity?.lastName ?? '',
    bio: identity?.bio ?? '',
    avatarUrl: identity?.avatarUrl ?? '',
});

const UpdateUserPage = () => {
    const notify = useNotify();
    const redirect = useRedirect();
    // const { data: identityData, isLoading } = useGetIdentity();
    const { data: identityData, isLoading, refetch } = useGetIdentity();
    const identity = identityData as UserIdentity | undefined;
    const [form, setForm] = useState<ProfileFormState>(emptyForm);
    const [submitting, setSubmitting] = useState(false);

    const initialForm = useMemo(() => mapIdentityToForm(identity ?? undefined), [identity]);

    useEffect(() => {
        setForm(initialForm);
    }, [initialForm]);

    const handleChange = (field: keyof ProfileFormState) => (event: ChangeEvent<HTMLInputElement>) => {
        setForm((prev) => ({ ...prev, [field]: event.target.value }));
    };

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setSubmitting(true);

        try {
            const res = await fetch(`${API_V1_URL}/me`, {
                method: 'PUT',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: form.email,
                    first_name: form.firstName,
                    last_name: form.lastName,
                    bio: form.bio,
                    avatar_url: form.avatarUrl,
                }),
            });

            if (!res.ok) {
                throw new Error('Failed to update profile');
            }
            await refetch();
            notify('Profile updated successfully');
            redirect('/profile');
        } catch (error) {
            console.error('Error updating profile', error);
            notify('Failed to update profile', { type: 'warning' });
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <Card component="form" onSubmit={handleSubmit} noValidate>
            <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2} flexWrap="wrap" gap={1}>
                    <Box>
                        <Typography variant="h5">Edit Profile</Typography>
                        <Typography variant="body2" color="text.secondary">
                            Update the information associated with your account.
                        </Typography>
                    </Box>
                    <Button component={RouterLink} to="/profile" variant="outlined" disabled={submitting}>
                        Cancel
                    </Button>
                </Box>

                <Stack spacing={2}>
                    <TextField
                        label="Username"
                        name="username"
                        value={form.username}
                        onChange={handleChange('username')}
                        fullWidth
                        required
                        disabled={isLoading || submitting}
                    />
                    <TextField
                        label="Email"
                        name="email"
                        type="email"
                        value={form.email}
                        onChange={handleChange('email')}
                        fullWidth
                        required
                        disabled={isLoading || submitting}
                    />
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                        <TextField
                            label="First Name"
                            name="firstName"
                            value={form.firstName}
                            onChange={handleChange('firstName')}
                            fullWidth
                            disabled={isLoading || submitting}
                        />
                        <TextField
                            label="Last Name"
                            name="lastName"
                            value={form.lastName}
                            onChange={handleChange('lastName')}
                            fullWidth
                            disabled={isLoading || submitting}
                        />
                    </Stack>
                    <TextField
                        label="Bio"
                        name="bio"
                        value={form.bio}
                        onChange={handleChange('bio')}
                        fullWidth
                        multiline
                        minRows={3}
                        disabled={isLoading || submitting}
                    />
                    <TextField
                        label="Avatar URL"
                        name="avatarUrl"
                        value={form.avatarUrl}
                        onChange={handleChange('avatarUrl')}
                        fullWidth
                        disabled={isLoading || submitting}
                    />
                </Stack>

                <Box display="flex" justifyContent="flex-end" mt={3}>
                    <Button type="submit" variant="contained" disabled={submitting || isLoading}>
                        {submitting ? 'Saving...' : 'Save Changes'}
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

export default UpdateUserPage;
