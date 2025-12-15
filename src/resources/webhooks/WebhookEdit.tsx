import {
    BooleanInput,
    Edit,
    SimpleForm,
    TextInput,
} from 'react-admin';
import { Card, CardContent, Typography } from '@mui/material';

const WebhookEdit = () => (
    <Card sx={{ mt: 4 }}>
        <CardContent>
            <Typography variant="h5" gutterBottom>
                Edit Webhook
            </Typography>
            <Edit mutationMode="pessimistic">
                <SimpleForm>
                    <TextInput source="name" label="Name" fullWidth required />
                    <TextInput source="description" label="Description" fullWidth multiline />
                    <TextInput source="type" label="Type" fullWidth />
                    <TextInput source="tickers" label="Tickers" fullWidth />
                    <BooleanInput source="active" label="Active" />
                </SimpleForm>
            </Edit>
        </CardContent>
    </Card>
);

export default WebhookEdit;
