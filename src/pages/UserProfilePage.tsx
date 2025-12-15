import { Button, Card, CardContent, TextField, Typography, Box, Stack } from '@mui/material';
import { useGetIdentity } from 'react-admin';
import { Link as RouterLink } from 'react-router-dom';
import type { UserIdentity } from '../types/user';

const getDisplayName = (identity?: UserIdentity) => {
    if (!identity) return '';
    if (identity.fullName?.trim()) return identity.fullName;
    return [identity.firstName, identity.lastName].filter(Boolean).join(' ');
};

export default function UserProfilePage() {
    // ✅ não passe <UserIdentity>; o genérico é do ERRO
    const { data: identityRaw, isLoading } = useGetIdentity();
    const identity = identityRaw as UserIdentity | undefined;

    const fullName = getDisplayName(identity);

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
                    <Button
                        variant="contained"
                        component={RouterLink}
                        to="/profile/edit"
                        disabled={isLoading}
                    >
                        Update Profile
                    </Button>
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
        </Card>
    );
}
