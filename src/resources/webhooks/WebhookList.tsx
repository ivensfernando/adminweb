import {
    BooleanInput,
    DateField,
    EditButton,
    Identifier,
    List,
    RaRecord,
    TextInput,
    useListContext,
} from 'react-admin';
import { Card, CardContent, Chip, Stack, Typography } from '@mui/material';

const webhookFilters = [
    <TextInput key="name" label="Search" source="name" alwaysOn />, 
    <BooleanInput key="active" label="Active" source="active" />,
];

type WebhookRecord = RaRecord<Identifier> & {
    id: Identifier;
    name?: string;
    description?: string;
    type?: string;
    tickers?: string;
    active?: boolean;
    created_at?: string;
};

const WebhookCards = () => {
    const { data, isLoading } = useListContext<WebhookRecord>();

    if (isLoading) {
        return <Typography>Carregando webhooks...</Typography>;
    }

    if (!data?.length) {
        return <Typography>Nenhum webhook encontrado.</Typography>;
    }

    return (
        <Stack spacing={2} mt={2}>
            {data.map((record) => (
                <Card key={record.id} variant="outlined" sx={{ borderRadius: 2 }}>
                    <CardContent>
                        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
                            <Stack spacing={0.5} flex={1}>
                                <Typography variant="h6">{record.name}</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {record.description || 'Sem descrição'}
                                </Typography>
                                <Stack direction="row" spacing={1} mt={1} flexWrap="wrap">
                                    <Chip label={record.type ? `Tipo: ${record.type}` : 'Tipo não informado'} size="small" />
                                    <Chip
                                        label={record.tickers ? `Tickers: ${record.tickers}` : 'Sem tickers definidos'}
                                        size="small"
                                    />
                                    <Chip
                                        label={record.active ? 'Ativo' : 'Inativo'}
                                        color={record.active ? 'success' : 'default'}
                                        size="small"
                                    />
                                </Stack>
                                <Typography variant="caption" color="text.secondary" mt={1} display="inline-flex" alignItems="center">
                                    Criado em&nbsp;
                                    <DateField source="created_at" record={record} />
                                </Typography>
                            </Stack>
                            <EditButton record={record} />
                        </Stack>
                    </CardContent>
                </Card>
            ))}
        </Stack>
    );
};

const WebhookList = () => (
    <Card sx={{ mt: 4 }}>
        <CardContent>
            <List
                filters={webhookFilters}
                sort={{ field: 'created_at', order: 'DESC' }}
                perPage={10}
            >
                <WebhookCards />
            </List>
        </CardContent>
    </Card>
);

export default WebhookList;
