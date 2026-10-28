const TAX_RATE = 0.22;

class ShoppingCart {
  #items = [];

  constructor(ownerName) {
    this.ownerName = ownerName;
  }

  addItem(productName, unitPrice, quantity = 1) {
    this.#items.push({ productName, unitPrice, quantity });
    return this;
  }

  get totalPrice() {
    return this.#items.reduce((acc, { unitPrice, quantity }) => acc + unitPrice * quantity, 0);
  }
}

function formatPrice(amount) {
  const withTax = amount * (1 + TAX_RATE);
  return `${withTax.toFixed(2)} EUR`;
}

const myCart = new ShoppingCart("Mario");
myCart.addItem("pizza", 8).addItem("birra", 4, 2);
console.log(myCart.ownerName, formatPrice(myCart.totalPrice));
