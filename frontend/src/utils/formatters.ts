import { format, formatDistanceToNow } from 'date-fns';
import { zhTW } from 'date-fns/locale';

export const formatTimestamp = (timestamp: number, formatStr: string = 'yyyy/MM/dd HH:mm'): string => {
    // Check if timestamp is in seconds (10 digits) or milliseconds (13 digits)
    // Backend seems to use seconds based on models.py (Integer)
    const date = new Date(timestamp * 1000);
    return format(date, formatStr, { locale: zhTW });
};

export const formatRelativeTime = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return formatDistanceToNow(date, { addSuffix: true, locale: zhTW });
};

export const truncateText = (text: string, maxLength: number): string => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
};
