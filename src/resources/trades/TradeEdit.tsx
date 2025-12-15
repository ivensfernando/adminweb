import {
    Create,
    Edit,
    SimpleForm,
    TextInput,
    NumberInput,
    DateInput,
    SelectInput,
} from 'react-admin';

const typeChoices = [
    { id: 'spot', name: 'Spot' },
    { id: 'futures', name: 'Futures' },
];

const TradeFormFields = () => (
    <>
        <TextInput source="symbol" />
        <SelectInput source="type" choices={typeChoices} />
        <NumberInput source="leverage" />
        <NumberInput source="entry_price" />
        <NumberInput source="exit_price" />
        <NumberInput source="fee" />
        <TextInput source="indicators" />
        <TextInput source="sentiment" />
        <NumberInput source="stop_loss" />
        <NumberInput source="take_profit" />
        <TextInput source="exchange" />
        <DateInput source="trade_date" />
    </>
);


const TradeEdit = () => (
    <Edit>
        <SimpleForm>
            <TradeFormFields />
        </SimpleForm>
    </Edit>
);

export default TradeEdit;
