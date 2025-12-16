import {
    Button,
    Card,
    CardContent,
    TextField,
    Typography,
    Box,
    Stack,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    DialogContentText,
} from '@mui/material';
import { useAuthenticated, useGetIdentity, useNotify } from 'react-admin';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { API_V1_URL } from '../config/api';
import type { UserIdentity } from '../types/user';

const getDisplayName = (identity?: UserIdentity) => {
    if (!identity) return '';
    if (identity.fullName?.trim()) return identity.fullName;
    return [identity.firstName, identity.lastName].filter(Boolean).join(' ');
};

export default function UserProfilePage() {
    useAuthenticated();
    const notify = useNotify();
    const navigate = useNavigate();
    // ✅ não passe <UserIdentity>; o genérico é do ERRO
    const { data: identityRaw, isLoading } = useGetIdentity();
    const identity = identityRaw as UserIdentity | undefined;

    const fullName = getDisplayName(identity);

    const [passwordModalOpen, setPasswordModalOpen] = useState(false);
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

    const passwordsMatch = newPassword.trim() !== '' && newPassword === confirmPassword;

    const resetModalState = () => {
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setErrorMessage('');
    };

    const handleCloseModal = () => {
        if (isSubmitting) return;
        setPasswordModalOpen(false);
        resetModalState();
    };

    const handleSubmitPasswordChange = async (event: React.FormEvent) => {
        event.preventDefault();
        setErrorMessage('');

        if (!passwordsMatch) {
            setErrorMessage('New passwords must match.');
            return;
        }
        setIsSubmitting(true);

        try {
            const response = await fetch(`${API_V1_URL}/me/change-password`, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                }),
            });

            if (!response.ok) {
                const message = (await response.text()) || 'Unable to change password.';
                throw new Error(message);
            }

            notify('Password updated successfully', { type: 'info' });
            resetModalState();
            setPasswordModalOpen(false);
            navigate('/login');
        } catch (error) {
            console.error('Failed to change password', error);
            setErrorMessage(error instanceof Error ? error.message : 'Unable to change password.');
        } finally {
            setIsSubmitting(false);
        }
    };

    // estilo para “duas colunas” no md+ (1 coluna no xs)
    const half = { width: { xs: '100%', md: 'calc(50% - 8px)' } };

    return (
        <Card>
            <CardContent>
                {/* Cabeçalho */}
                <Box
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    mb={2}
                    flexWrap="wrap"
                    gap={1}
                >
                    <Box>
                        <Typography variant="h5">User Profile</Typography>
                        <Typography variant="body2" color="text.secondary">
                            Manage the information associated with your account.
                        </Typography>
                    </Box>
                    <Stack direction="row" spacing={1}>
                        <Button
                            variant="outlined"
                            onClick={() => setPasswordModalOpen(true)}
                            disabled={isLoading}
                        >
                            Change Password
                        </Button>
                        <Button
                            variant="contained"
                            component={RouterLink}
                            to="/profile/edit"
                            disabled={isLoading}
                        >
                            Update Profile
                        </Button>
                    </Stack>
                </Box>

                {/* Campos (Stack = sem Grid) */}
                <Stack direction="row" flexWrap="wrap" gap={2}>
                    <Box sx={half}>
                        <TextField label="Full Name" value={fullName} InputProps={{ readOnly: true }} fullWidth margin="normal" />
                    </Box>
                    <Box sx={half}>
                        <TextField label="Username" value={identity?.username ?? ''} InputProps={{ readOnly: true }} fullWidth margin="normal" />
                    </Box>
                    <Box sx={half}>
                        <TextField label="Email" value={identity?.email ?? ''} InputProps={{ readOnly: true }} fullWidth margin="normal" />
                    </Box>
                    <Box sx={half}>
                        <TextField label="First Name" value={identity?.firstName ?? ''} InputProps={{ readOnly: true }} fullWidth margin="normal" />
                    </Box>
                    <Box sx={half}>
                        <TextField label="Last Name" value={identity?.lastName ?? ''} InputProps={{ readOnly: true }} fullWidth margin="normal" />
                    </Box>
                </Stack>
            </CardContent>
            <Dialog open={passwordModalOpen} onClose={handleCloseModal} fullWidth maxWidth="xs">
                <Box component="form" onSubmit={handleSubmitPasswordChange} noValidate>
                    <DialogTitle>Change Password</DialogTitle>
                    <DialogContent>
                        <DialogContentText mb={2}>
                            Enter your current password and choose a new one. You will be redirected to the login page after a
                            successful update.
                        </DialogContentText>
                        <Stack spacing={2}>
                            <TextField
                                label="Current Password"
                                type="password"
                                value={currentPassword}
                                onChange={(event) => setCurrentPassword(event.target.value)}
                                required
                                fullWidth
                                autoFocus
                            />
                            <TextField
                                label="New Password"
                                type="password"
                                value={newPassword}
                                onChange={(event) => setNewPassword(event.target.value)}
                                required
                                fullWidth
                            />
                            <TextField
                                label="Confirm New Password"
                                type="password"
                                value={confirmPassword}
                                onChange={(event) => setConfirmPassword(event.target.value)}
                                required
                                fullWidth
                                error={Boolean(confirmPassword) && !passwordsMatch}
                                helperText={
                                    Boolean(confirmPassword) && !passwordsMatch
                                        ? 'New passwords must match.'
                                        : ' '
                                }
                            />
                            {errorMessage && (
                                <Typography color="error" variant="body2">
                                    {errorMessage}
                                </Typography>
                            )}
                        </Stack>
                    </DialogContent>
                    <DialogActions sx={{ px: 3, pb: 3 }}>
                        <Button onClick={handleCloseModal} disabled={isSubmitting}>
                            Cancel
                        </Button>
                        <Button
                            type="submit"
                            variant="contained"
                            disabled={!passwordsMatch || isSubmitting || !currentPassword.trim()}
                        >
                            {isSubmitting ? 'Updating...' : 'Update Password'}
                        </Button>
                    </DialogActions>
                </Box>
            </Dialog>
        </Card>
    );
}
