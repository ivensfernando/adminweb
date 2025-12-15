import {
  List,
  Datagrid,
  TextField,
  Edit,
  SimpleForm,
  TextInput,
  Create,
  DateField,
  DateInput,
  NumberField,
  NumberInput,
} from 'react-admin';

export const TradeList = () => (
  <List>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <DateField source="date" />
      <TextField source="asset" />
      <NumberField source="entry_price" />
      <NumberField source="exit_price" />
    </Datagrid>
  </List>
);

export const TradeEdit = () => (
  <Edit>
    <SimpleForm>
      <DateInput source="date" />
      <TextInput source="asset" />
      <NumberInput source="entry_price" />
      <NumberInput source="exit_price" />
    </SimpleForm>
  </Edit>
);

export const TradeCreate = () => (
  <Create>
    <SimpleForm>
      <DateInput source="date" />
      <TextInput source="asset" />
      <NumberInput source="entry_price" />
      <NumberInput source="exit_price" />
    </SimpleForm>
  </Create>
);
