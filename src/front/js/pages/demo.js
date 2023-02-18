import React, { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";

import { Context } from "../store/appContext";

export const Demo = () => {
  const { store, actions } = useContext(Context);

  const submitPhoto = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    let url = process.env.BACKEND_URL;
    let response = await fetch(url + "/api/uploadPhoto", {
      body: formData,
      method: "POST",
      headers: {
        Authorization: "Bearer " + store.token,
      },
    });
    if (response.ok) {
      console.log("Imagen cargada");
      actions.getPhoto();
    } else {
      console.error(response.statusText);
    }
  };

  return (
    <div className="container">
      <div className="mb-3">
        <img src={store.profilePic.signed_url} />
        <label htmlFor="formFile" className="form-label">
          Default file input example
        </label>
        <form onSubmit={submitPhoto}>
          <input
            className="form-control"
            type="file"
            id="formFile"
            name="profilePic"
          ></input>
          <button className="btn btn-primary" type="submit">
            Enviar
          </button>
        </form>
      </div>
    </div>
  );
};
