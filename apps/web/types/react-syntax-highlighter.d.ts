declare module "react-syntax-highlighter" {
    import { ComponentType, ReactNode } from "react";

    export interface SyntaxHighlighterProps {
        children?: string | string[];
        style?: { [key: string]: React.CSSProperties };
        language?: string;
        PreTag?: string | ComponentType<any>;
        customStyle?: React.CSSProperties;
        [key: string]: any;
    }

    export const Prism: ComponentType<SyntaxHighlighterProps>;
    export const Light: ComponentType<SyntaxHighlighterProps>;
    export default ComponentType<SyntaxHighlighterProps>;
}

declare module "react-syntax-highlighter/dist/esm/styles/prism" {
    const atomDark: { [key: string]: React.CSSProperties };
    const oneDark: { [key: string]: React.CSSProperties };
    const vscDarkPlus: { [key: string]: React.CSSProperties };
    const dracula: { [key: string]: React.CSSProperties };
    const materialDark: { [key: string]: React.CSSProperties };
    export { atomDark, oneDark, vscDarkPlus, dracula, materialDark };
}

declare module "react-syntax-highlighter/dist/cjs/styles/prism" {
    const atomDark: { [key: string]: React.CSSProperties };
    const oneDark: { [key: string]: React.CSSProperties };
    const vscDarkPlus: { [key: string]: React.CSSProperties };
    const dracula: { [key: string]: React.CSSProperties };
    const materialDark: { [key: string]: React.CSSProperties };
    export { atomDark, oneDark, vscDarkPlus, dracula, materialDark };
}
