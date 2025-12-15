export type UserIdentity = {
    id: string | number;
    username: string;
    email: string;
    firstName?: string;
    lastName?: string;
    fullName?: string;
    bio?: string;
    avatarUrl?: string;
    createdAt?: string;
    updatedAt?: string;
};
