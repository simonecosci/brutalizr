using System;
using System.Collections.Generic;
using System.Linq;

namespace Shop.Orders
{
    public class OrderProcessor
    {
        private const decimal ShippingCost = 4.99m;
        private readonly List<decimal> _orderTotals = new List<decimal>();

        public string StoreName { get; set; }

        public OrderProcessor(string storeName)
        {
            StoreName = storeName;
        }

        public void RegisterOrder(decimal amount, bool expressDelivery = false)
        {
            var finalAmount = expressDelivery ? amount + ShippingCost : amount;
            _orderTotals.Add(finalAmount);
        }

        public decimal GrandTotal() => _orderTotals.Sum();

        public static void Main(string[] args)
        {
            var processor = new OrderProcessor("Bottega");
            processor.RegisterOrder(20m, true);
            Console.WriteLine($"{processor.StoreName}: {processor.GrandTotal()}");
        }
    }
}
