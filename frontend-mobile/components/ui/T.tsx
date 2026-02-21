import React from 'react';
import { Text, TextProps } from 'react-native';
import { useLanguage } from '../../context/LanguageContext';

/**
 * A handy Text component that automatically translates itself.
 * Usage: <T>hello_world</T> -> Renders "Hello World" or "नमस्ते दुनिया"
 */
export const T = ({ children, style, ...props }: TextProps & { children: string }) => {
    const { t } = useLanguage();

    // Ask the translator for the meaning of this word key
    const translatedText = t(children as any);

    return (
        <Text style={style} {...props}>
            {translatedText}
        </Text>
    );
};
