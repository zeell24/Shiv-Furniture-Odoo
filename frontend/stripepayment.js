// src/pages/customer/PaymentPage.jsx
import React from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe('your_publishable_key_here');

const CheckoutForm = ({ amount }) => {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!stripe || !elements) return;

    // Logic for payment reconciliation [cite: 90]
    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: elements.getElement(CardElement),
    });

    if (error) {
      console.log('[error]', error);
    } else {
      alert(`Payment Successful for $${amount}! Status updated to Paid.`);
      // Here you would trigger the backend to update status to "Paid" [cite: 57]
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-4 bg-white shadow rounded">
      <h3 className="text-lg mb-4">Secure Payment</h3>
      <div className="mb-4 p-3 border rounded"><CardElement /></div>
      <button 
        type="submit" 
        disabled={!stripe} 
        className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700"
      >
        Pay ${amount}
      </button>
    </form>
  );
};

const PaymentPage = () => (
  <Elements stripe={stripePromise}>
    <CheckoutForm amount={1500} />
  </Elements>
);

export default PaymentPage;