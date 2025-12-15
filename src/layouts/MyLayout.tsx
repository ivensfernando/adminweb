import { Layout, LayoutProps } from 'react-admin';
import MyAppBar from './MyAppBar';
import MyFooter from './MyFooter';
import { Box } from '@mui/material';

const MyLayout = (props: LayoutProps) => (
    <Box
        display="flex"
        flexDirection="column"
        minHeight="100vh"
    >
        {/* This box grows with content */}
        <Box flex="1" display="flex" flexDirection="column">
            <Layout
                {...props}
                appBar={MyAppBar}
                menu={() => null}
                sidebar={() => null}
                sx={{
                    '& .RaLayout-appFrame': {
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        minHeight: '100vh',
                        marginTop: 0, // 💡 This is critical to remove the white space
                    },
                    '& .RaLayout-contentWithSidebar': {
                        display: 'flex',
                        flexDirection: 'column',
                        flex: 1,
                    },
                    '& main': {
                        display: 'flex',
                        flexDirection: 'column',
                        flex: 1,
                    },
                    '& .RaLayout-content': {
                        flex: 1,
                    },
                }}
            />
        </Box>

        {/* Always at the bottom */}
        <MyFooter />
    </Box>
);

export default MyLayout;
