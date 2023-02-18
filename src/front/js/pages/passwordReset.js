import React, { useState } from "react";

export const PasswordRequest = (props) => {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  async function sendRequest(e) {
    e.preventDefault();
    const req = await fetch(
      process.env.BACKEND_URL + "/api/requestresetpassword",
      {
        method: "POST",
        body: JSON.stringify({ email }),
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    if (!req.ok) {
      console.error(req.statusText);
      return;
    }
    setMessage("Solicitud de reinicio de clave enviada");
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
          <label for="exampleInputEmail1" className="form-label">
            Email
          </label>
          <input
            type="email"
            className="form-control"
            id="exampleInputEmail1"
            aria-describedby="emailHelp"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <div id="emailHelp" className="form-text">
            We'll never share your email with anyone else.
          </div>
        </div>
        <button type="submit" className="btn btn-primary">
          Submit
        </button>
      </form>
    </div>
  );
};
