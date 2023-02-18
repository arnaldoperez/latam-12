// Import the functions you need from the SDKs you need
import {
    initializeApp
} from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBxmfsAS-mti1jpEBRhrL7YmrAGzoMem3Y",
    authDomain: "clase-imagenes-flask.firebaseapp.com",
    projectId: "clase-imagenes-flask",
    storageBucket: "clase-imagenes-flask.appspot.com",
    messagingSenderId: "105819654230",
    appId: "1:105819654230:web:ab9d149445b776c07d93f7"
};

// Initialize Firebase
const firebaseApp = initializeApp(firebaseConfig);
export default firebaseApp