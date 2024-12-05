# GerPS-HIL Frontend

Everything you need to build a Svelte project, powered by [`create-svelte`](https://github.com/sveltejs/kit/tree/master/packages/create-svelte).


## Docker

> this can also be used for development, but live preview will not work

> the Dockerfile is supposed to be used for deployment (compiles web app & serves it)

- build the container using `sudo docker build -t svelte .`
- run the container using  `sudo docker run -p 3000:3000 svelte`
- you can now access the frontend in your browser using `localhost:3000`
    - (port might have changed, check the Dockerfile)  

## Development
`
Requirements:
- installed `npm`
- `node` version 23.2.0 installed (recommended: use `nvm` to manage node versions)


1. Clone the repository 
2. `cd frontend`
3. `npm install` (install dependencies listed in `package.json`)
4. `npm run dev` to start the webserver
5. access website at http://localhost:5173

## Building

To create a production version of your app:

```bash
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://kit.svelte.dev/docs/adapters) for your target environment.
