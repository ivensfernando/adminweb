import { useMemo, useState } from 'react';
import {
    BooleanInput,
    Create,
    SimpleForm,
    TextInput,
    useNotify,
} from 'react-admin';
import {
    Box,
    Button,
    Card,
    CardContent,
    Stack,
    Typography,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

export type CreatedWebhook = {
    id?: number;
    name?: string;
    token?: string;
    url?: string;
    fullUrl?: string;
};

const maskToken = (token?: string) => {
    if (!token) return '';
    const visible = Math.ceil(token.length / 2);
    const hidden = token.length - visible;
    return `${token.slice(0, visible)}${'•'.repeat(hidden)}`;
};

const WebhookUrlPreview = ({ created }: { created?: CreatedWebhook }) => {
    const notify = useNotify();
    const maskedUrl = useMemo(() => {
        if (!created) return '';
        if (created.fullUrl && created.token) {
            return created.fullUrl.replace(created.token, maskToken(created.token));
        }
        if (created.url && created.token) {
            const normalizedUrl = created.url.replace(/\/$/, '');
            return `${normalizedUrl}/${maskToken(created.token)}`;
        }
        return created.fullUrl ?? created.url ?? '';
    }, [created]);

    const copyFullUrl = async () => {
        if (!created?.fullUrl && !(created?.url && created?.token)) {
            return;
        }
        const fullUrl = created.fullUrl ?? `${created.url?.replace(/\/$/, '')}/${created.token}`;
        try {
            await navigator.clipboard.writeText(fullUrl ?? '');
            notify('Webhook URL copied');
        } catch (error) {
            console.error('Failed to copy webhook URL', error);
            notify('Unable to copy URL', { type: 'warning' });
        }
    };

    if (!created) return null;

    return (
        <Box mt={3} p={2} borderRadius={2} bgcolor="background.paper" boxShadow={1}>
            <Typography variant="h6" gutterBottom>
                Webhook URL
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
                Copie este endereço para enviar alertas. O token está parcialmente oculto para segurança.
            </Typography>
            <Box
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                p={2}
                borderRadius={1}
                bgcolor="background.default"
            >
                <Typography component="code" sx={{ fontFamily: 'monospace', wordBreak: 'break-all', mr: 2 }}>
                    {maskedUrl}
                </Typography>
                <Button variant="contained" startIcon={<ContentCopyIcon />} onClick={copyFullUrl}>
                    Copiar URL
                </Button>
            </Box>
        </Box>
    );
};

const WebhookCreate = () => {
    const notify = useNotify();
    const [createdWebhook, setCreatedWebhook] = useState<CreatedWebhook | undefined>();

    return (
        <Card sx={{ mt: 4 }}>
            <CardContent>
                <Typography variant="h5" gutterBottom>
                    Criar Webhook
                </Typography>
                <Create
                    mutationOptions={{
                        onSuccess: (data) => {
                            setCreatedWebhook(data as CreatedWebhook);
                            notify('Webhook criado com sucesso');
                        },
                    }}
                >
                    <SimpleForm>
                        <Stack spacing={2}>
                            <TextInput source="name" label="Name" fullWidth required />
                            <TextInput source="description" label="Description" fullWidth multiline />
                            <TextInput source="type" label="Type" fullWidth />
                            <TextInput source="tickers" label="Tickers" fullWidth helperText="Separe múltiplos símbolos por vírgula" />
                            <BooleanInput source="active" label="Active" />
                        </Stack>
                    </SimpleForm>
                </Create>

                <WebhookUrlPreview created={createdWebhook} />
            </CardContent>
        </Card>
    );
};

export default WebhookCreate;
