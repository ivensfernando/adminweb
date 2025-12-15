import { NumberInput, TextInput } from 'react-admin';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import PasteTextArea from "../PasteTextArea";

const TradeDetailsForm = () => {

    return (
        <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 2, boxShadow: 1 }}>
            <Typography variant="h6" gutterBottom>Trade Details</Typography>


            <PasteTextArea source="notes" label="Notes" />
        </Box>
    );


};

export default TradeDetailsForm;


