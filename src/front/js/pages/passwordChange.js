import React, { useState } from "react";
import { useSearchParams } from "react-router-dom";

export const PasswordChange = (props) => {
  const [password, setPassword] = useState("");
  const [verify, setVerify] = useState("");
  const [message, setMessage] = useState("");
  let [searchParams, setSearchParams] = useSearchParams();

  async function sendRequest(e) {
    e.preventDefault();

    if (password != verify) {
      setMessage("Las claves no coinciden");
      return;
    }
    const token = searchParams.get("token");
    const req = await fetch(process.env.BACKEND_URL + "/api/resetpassword", {
      method: "POST",
      body: JSON.stringify({ password }),
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
    });
    if (!req.ok) {
      console.error(req.statusText);
      return;
    }
    setMessage("Clave cambiada");
  }

  return (
    <div className="container-flex">
      {message ? (
        <div class="alert alert-success" role="alert">
          {message}
        </div>
      ) : (
        ""
      )}
      <form onSubmit={sendRequest}>
        <div className="mb-3">
          <label for="password" className="form-label">
            Inserte clave
          </label>
          <input
            type="password"
            className="form-control"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label for="verify" className="form-label">
            Verifque su clave
          </label>
          <input
            type="password"
            className="form-control"
            id="verify"
            value={verify}
            onChange={(e) => setVerify(e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary">
          Submit
        </button>
      </form>
    </div>
  );
};
