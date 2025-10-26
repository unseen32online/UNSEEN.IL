import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { CartProvider } from "./context/CartContext";
import { Toaster } from "./components/ui/sonner";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import CollectionPage from "./pages/CollectionPage";
import ProductDetail from "./pages/ProductDetail";
import Cart from "./pages/Cart";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import ContactUs from "./pages/ContactUs";
import Checkout from "./pages/Checkout";
import OrderConfirmation from "./pages/OrderConfirmation";
import AdminDashboard from "./pages/AdminDashboard";

function App() {
  return (
    <CartProvider>
      <div className="App">
        <BrowserRouter>
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/collection/:category" element={<CollectionPage />} />
            <Route path="/product/:id" element={<ProductDetail />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={<Checkout />} />
            <Route path="/order-confirmation/:orderNumber" element={<OrderConfirmation />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/contact" element={<ContactUs />} />
          </Routes>
          <Footer />
        </BrowserRouter>
        <Toaster />
      </div>
    </CartProvider>
  );
}

export default App;
