import { Typography, Box } from '@mui/material';

const MyFooter = () => (
    <Box
        component="footer"
        p={2}
        textAlign="center"
        bgcolor="background.paper"
        borderTop="1px solid #ccc"
    >
        <Typography variant="body2" color="textSecondary">
            © 2025 Biidin Admin
        </Typography>
    </Box>
);

export default MyFooter;
