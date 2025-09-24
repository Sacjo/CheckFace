import React, { useState } from "react";

function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("http://localhost:5000/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (res.ok) {
      setMessage("Usuario creado exitosamente. Ya puede iniciar sesión.");
    } else {
      setMessage(data.error);
    }
  };

  return (
    <div className="bg-light d-flex align-items-center vh-100">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-xl-4 col-lg-6 col-md-8">
            <div className="card shadow-lg border-0 rounded-lg mt-5">
              <div className="card-header">
                <h3 className="text-center font-weight-light my-4">
                  Registro de Usuario
                </h3>
              </div>
              <div className="card-body">
                {message && <div className="alert alert-info">{message}</div>}
                <form onSubmit={handleSubmit}>
                  <div className="form-group mb-3">
                    <label className="small mb-1">Username</label>
                    <input
                      type="text"
                      className="form-control"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group mb-3">
                    <label className="small mb-1">Password</label>
                    <input
                      type="password"
                      className="form-control"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  <button type="submit" className="btn btn-success w-100">
                    Registrar
                  </button>
                </form>
              </div>
              <div className="card-footer text-center">
                <a href="/login">Volver al login</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;
