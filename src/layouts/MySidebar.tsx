import { Menu, useSidebarState} from 'react-admin';
import { Drawer , Theme, useMediaQuery} from '@mui/material';

const drawerWidth = 240;

const MySidebar = () => {
    const [open, setOpen] = useSidebarState();
    const isSmall = useMediaQuery((theme: Theme) => theme.breakpoints.down('sm'));
    return (
        <Drawer
            variant={isSmall ? 'temporary' : 'permanent'}
            open={open}
            onClose={() => setOpen(false)}
            ModalProps={{
                keepMounted: true, // improves performance on mobile
            }}
            sx={{
                '& .MuiDrawer-paper': {
                    width: drawerWidth,
                },
            }}
        >
            <Menu />
        </Drawer>
    );
};

export default MySidebar;

