import React from "react";

import axios from "axios";

const scopes = ["username", "payments"];

const onIncompletePaymentFound = (payment: PaymentDTO) => {
  console.log("onIncompletePaymentFound", payment);
  return axiosClient.post("/incomplete", { payment }.config);
};

const config = {
  headers: {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
  },
};

const authResult = await window.Pi.authenticate(
  scopes,
  onIncompletePaymentFound
);

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_SERVER_URL,
  timeout: 20000,
});

const ProductBox = () => {
  return (
    <>
      <div>ProductBox</div>
    </>
  );
};

export default ProductBox;
