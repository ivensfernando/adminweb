import {
    DateField,
    Identifier,
    List,
    NumberField,
    RaRecord,
    ReferenceField,
    ReferenceInput,
    SelectInput,
    ShowButton,
    TextField,
    TextInput,
    useListContext,
} from 'react-admin';
import { Card, CardContent, Stack, Typography } from '@mui/material';

const alertFilters = [
    <ReferenceInput key="webhook" label="Webhook" source="webhook_id" reference="webhooks" alwaysOn>
        <SelectInput optionText="name" />
    </ReferenceInput>,
    <TextInput key="ticker" label="Ticker" source="ticker" alwaysOn />,
];

type WebhookAlertRecord = RaRecord<Identifier> & {
    id: Identifier;
    webhook_id?: number | string;
    ticker?: string;
    action?: string;
    sentiment?: string;
    quantity?: number;
    price?: number;
    interval?: string;
    received_at?: string;
};

const WebhookAlertCards = () => {
    const { data, isLoading } = useListContext<WebhookAlertRecord>();

    if (isLoading) {
        return <Typography>Carregando alertas...</Typography>;
    }

    if (!data?.length) {
        return <Typography>Nenhum alerta encontrado.</Typography>;
    }

    return (
        <Stack spacing={2} mt={2}>
            {data.map((record) => (
                <Card key={record.id} variant="outlined" sx={{ borderRadius: 2 }}>
                    <CardContent>
                        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
                            <Stack spacing={0.5} flex={1}>
                                <Typography variant="h6">{record.ticker}</Typography>
                                <Stack direction="row" spacing={1} flexWrap="wrap">
                                    <ReferenceField source="webhook_id" reference="webhooks" record={record} label="Webhook">
                                        <TextField source="name" />
                                    </ReferenceField>
                                    <TextField source="action" record={record} label="Ação" />
                                    <TextField source="sentiment" record={record} label="Sentimento" />
                                    <TextField source="interval" record={record} label="Intervalo" />
                                </Stack>
                                <Stack direction="row" spacing={2} mt={1} flexWrap="wrap">
                                    <Typography variant="body2">
                                        Quantidade: <NumberField source="quantity" record={record} />
                                    </Typography>
                                    <Typography variant="body2">
                                        Preço: <NumberField source="price" record={record} />
                                    </Typography>
                                </Stack>
                                <Typography variant="caption" color="text.secondary" display="inline-flex" alignItems="center">
                                    Recebido em&nbsp;
                                    <DateField source="received_at" record={record} />
                                </Typography>
                            </Stack>
                            <ShowButton record={record} />
                        </Stack>
                    </CardContent>
                </Card>
            ))}
        </Stack>
    );
};

const WebhookAlertList = () => (
    <Card sx={{ mt: 4 }}>
        <CardContent>
            <List
                filters={alertFilters}
                sort={{ field: 'received_at', order: 'DESC' }}
                perPage={10}
            >
                <WebhookAlertCards />
            </List>
        </CardContent>
    </Card>
);

export default WebhookAlertList;
