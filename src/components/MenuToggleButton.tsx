import { IconButton } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useSidebarState } from 'react-admin';

export const MenuToggleButton = () => {
    const [open, setOpen] = useSidebarState();
    return (
        <IconButton color="inherit" onClick={() => setOpen(!open)}>
            <MenuIcon />
        </IconButton>
    );
};
