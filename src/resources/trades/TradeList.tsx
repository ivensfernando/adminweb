import {
    List,
    Datagrid,
    TextField,
    NumberField,
    DateField,
    TextInput,
    DateInput,
    downloadCSV,
    TopToolbar,
    CreateButton, useListContext,
} from 'react-admin';
import {Box, Paper, Button} from '@mui/material';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import TableViewIcon from '@mui/icons-material/TableView';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';



const CustomExportButtons = () => {
    const {data} = useListContext();

    const exportPDF = () => {


        const doc = new jsPDF();
        doc.text('Trades Export', 14, 16);
        autoTable(doc, {
            startY: 20,
            head: [['Id', 'Symbol', 'Type', 'Entry', 'Exit', 'Leverage', 'Exchange', 'Date']],
            body: data?.map((record: any) => [
                record.id,
                record.symbol,
                record.type,
                record.entry_price,
                record.exit_price,
                record.leverage,
                record.exchange,
                record.trade_date
            ]),
        });
        doc.save('trades.pdf');
    };
//
    const exportCSV = () => {
        if (!data) return;

        const headers = ['Id', 'Symbol', 'Type', 'Entry', 'Exit', 'Leverage', 'Exchange', 'Date'];
        const rows = data.map((record: any) =>
            [record.id, record.symbol, record.type, record.entry_price, record.exit_price, record.leverage, record.exchange, record.trade_date]
        );

        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.join(','))
        ].join('\n');

        const blob = new Blob([csvContent], {type: 'text/csv;charset=utf-8;'});
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.setAttribute('download', 'trades.csv');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <>
            <Button onClick={exportPDF} startIcon={<PictureAsPdfIcon />} size="small">Export PDF</Button>
            <Button onClick={exportCSV} startIcon={<TableViewIcon />} size="small">Export CSV</Button>
        </>
    );
};


// const ExportPdfButton = ({ data }: { data: any[] }) => {
//     const handleExport = () => {
//         const doc = new jsPDF();
//         autoTable(doc, {
//             head: [['ID', 'Symbol', 'Type', 'Entry', 'Exit', 'Leverage', 'Exchange', 'Date']],
//             body: data.map((record) => [
//                 record.id,
//                 record.symbol,
//                 record.type,
//                 record.entry_price,
//                 record.exit_price,
//                 record.leverage,
//                 record.exchange,
//                 record.trade_date
//             ]),
//         });
//         doc.save('trades.pdf');
//     };
//
//     return (
//         <Button onClick={handleExport} startIcon={<PictureAsPdfIcon />} size="small">
//             Export PDF
//         </Button>
//     );
// };

// const ExportCsvButton = ({ data }: { data: any[] }) => {
//     const handleExport = () => {
//         const csv = data.map((record) => ({
//             ID: record.id,
//             Symbol: record.symbol,
//             Type: record.type,
//             Entry: record.entry_price,
//             Exit: record.exit_price,
//             Leverage: record.leverage,
//             Exchange: record.exchange,
//             Date: record.trade_date,
//         }));
//         downloadCSV(csv, 'trades');
//     };
//
//     return (
//         <Button onClick={handleExport} startIcon={<TableViewIcon />} size="small">
//             Export CSV
//         </Button>
//     );
// };

// const TradeListActions = ({ data }: { data: any[] }) => (
//     <TopToolbar>
//         CreateButton />
//         <ExportPdfButton data={data} />
//         <ExportCsvButton data={data} />
//     </TopToolbar>
// );

const TradeListActions = () => (
    <TopToolbar>
        <CreateButton/>
        <CustomExportButtons/>
    </TopToolbar>
);

const TradeFilter = [
    <TextInput label="Search by Asset" source="asset" alwaysOn/>,
    <DateInput label="From Date" source="date_gte"/>,
    <DateInput label="To Date" source="date_lte"/>,
];

const TradeList = () => (
    <Box p={2}>
        <Paper
            elevation={3}
            sx={{
                position: 'relative',
                paddingBottom: 3, // space for the bottom bar
                paddingTop: 3,
                borderRadius: 2,
                overflow: 'hidden',
                marginTop: 4,
            }}
        >
            <List actions={<TradeListActions/>}>
                <Datagrid rowClick="edit">
                    <DateField source="trade_date"/>
                    <TextField source="exchange"/>
                    <TextField source="type"/>
                    <TextField source="contract_type"/>
                    <TextField source="symbol"/>
                    <NumberField source="leverage"/>
                    <NumberField source="price"/>
                    <NumberField source="exit_price"/>
                </Datagrid>
            </List>
            <Box
                sx={(theme) => ({
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    width: '100%',
                    height: '40px',
                    bgcolor: theme.palette.mode === 'dark' ? 'blueviolet' : 'blue',
                })}
            />
        </Paper>
    </Box>
);

export default TradeList;
