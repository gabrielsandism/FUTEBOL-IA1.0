import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content="⚽ Football Scanner AI - Real-time match analysis system" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='75' font-size='75'>⚽</text></svg>" />
      </Head>
      <body className="bg-dark-900 text-dark-50">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
