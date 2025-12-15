import {
    DateField,
    ListButton,
    NumberField,
    ReferenceField,
    Show,
    SimpleShowLayout,
    TextField,
    TopToolbar,
} from 'react-admin';
import { Card, CardContent, Typography } from '@mui/material';

const AlertShowActions = () => (
    <TopToolbar>
        <ListButton label="Voltar" />
    </TopToolbar>
);

const WebhookAlertShow = () => (
    <Card sx={{ mt: 4 }}>
        <CardContent>
            <Typography variant="h5" gutterBottom>
                Detalhes do Alerta
            </Typography>
            <Show actions={<AlertShowActions />}>
                <SimpleShowLayout>
                    <ReferenceField source="webhook_id" reference="webhooks" label="Webhook">
                        <TextField source="name" />
                    </ReferenceField>
                    <TextField source="ticker" label="Ticker" />
                    <TextField source="action" label="Action" />
                    <TextField source="sentiment" label="Sentiment" />
                    <NumberField source="quantity" label="Quantity" />
                    <NumberField source="price" label="Price" />
                    <TextField source="interval" label="Interval" />
                    <DateField source="alert_time" label="Alert Time" />
                    <DateField source="received_at" label="Received At" />
                </SimpleShowLayout>
            </Show>
        </CardContent>
    </Card>
);

export default WebhookAlertShow;
