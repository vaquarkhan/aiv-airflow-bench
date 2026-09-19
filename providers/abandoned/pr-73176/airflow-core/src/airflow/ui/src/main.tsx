Reflect.set(globalThis, "ChakraUI", ChakraUI);
Reflect.set(globalThis, "EmotionReact", EmotionReact);

// redirect to login page if the API responds with unauthorized or forbidden errors
axios.interceptors.response.use(
  (response) => response,
      globalThis.location.replace(`${loginPath}?${params.toString()}`);
    }

    return Promise.reject(error);
  },
);
