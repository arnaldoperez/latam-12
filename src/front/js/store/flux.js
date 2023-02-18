const getState = ({
  getStore,
  getActions,
  setStore
}) => {
  return {
    store: {
      message: null,
      token: "",
      profilePic: "",
      demo: [{
          title: "FIRST",
          background: "white",
          initial: "white",
        },
        {
          title: "SECOND",
          background: "white",
          initial: "white",
        },
      ],
    },
    actions: {
      // Use getActions to call a function within a fuction
      exampleFunction: () => {
        getActions().changeColor(0, "green");
      },
      refreshToken: async () => {
        // Token has expired
      },
      getAuthorizationHeaders: async () => {
        let {
          token
        } = getStore
        return {
          Authorization: "Bearer " + token
        }

      },
      getMessage: async () => {
        try {
          // fetching data from the backend
          const resp = await fetch(process.env.BACKEND_URL + "/api/hello");
          const data = await resp.json();
          setStore({
            message: data.message
          });
          // don't forget to return something, that is how the async resolves
          return data;
        } catch (error) {
          console.log("Error loading message from backend", error);
        }
      },
      changeColor: (index, color) => {
        //get the store
        const store = getStore();

        //we have to loop the entire demo array to look for the respective index
        //and change its color
        const demo = store.demo.map((elm, i) => {
          if (i === index) elm.background = color;
          return elm;
        });

        //reset the global store
        setStore({
          demo: demo
        });
      },
      fetchGenerico: async (endpoint, data, metodo) => {
        let url = process.env.BACKEND_URL;
        let response = await fetch(url + endpoint, {
          method: metodo,
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(data),
        });
        return response;
      },
      login: async (data) => {
        let url = process.env.BACKEND_URL;
        console.log(url);
        let response = await fetch(url + "/api/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(data),
        });
        let responseJson = await response.json();
        console.log(responseJson.token);
        let accessToken = responseJson.accessToken;
        let refreshToken = responseJson.refreshToken;

        setStore({
          token: token
        }); //reseteo todo el store
        getActions().getPhoto()
        return response;
      },
      getPhoto: async () => {
        let url = process.env.BACKEND_URL;
        let {
          token
        } = getStore()
        let {
          getAuthorizationHeaders
        } = getActions()
        let picResponse = await fetch(url + "/api/getPhoto", {
          method: "GET",
          headers: {
            ...getAuthorizationHeaders(),
            "Access-Control-Allow-Origin": "*"
          },
        });
        let profilePic = (await picResponse.json()).pictureUrl;
        setStore({
          profilePic
        });
      },
      fetchProtegido: async (endpoint, data = undefined, metodo = "GET") => {
        const store = getStore();
        let url = process.env.URL_BACKEND;
        let encabezado = {
          method: metodo,
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + store.token,
          },
          body: data ? JSON.stringify(data) : undefined,
        };

        let response = await fetch(url + endpoint, encabezado);
        return response;
      },
      setToken(token) {
        setStore({
          token
        })
      }
    },
  };
};

export default getState;