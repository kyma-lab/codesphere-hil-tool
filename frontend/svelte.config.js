import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      // You can specify Node adapter options here
      // For most projects, the default options are fine
      out: 'build' // This option specifies the output directory (optional)
    })
  }
};

export default config;
