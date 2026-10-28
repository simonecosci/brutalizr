import java.util.ArrayList;
import java.util.List;

public class InvoiceCalculator {
    private static final double VAT_RATE = 0.22;
    private final List<Double> lineAmounts = new ArrayList<>();

    public InvoiceCalculator addLine(double unitPrice, int quantity) {
        lineAmounts.add(unitPrice * quantity);
        return this;
    }

    public double computeTotal() {
        double subtotal = 0;
        for (double lineAmount : lineAmounts) {
            subtotal += lineAmount;
        }
        return subtotal * (1 + VAT_RATE);
    }

    @Override
    public String toString() {
        return "InvoiceCalculator lines=" + lineAmounts.size();
    }

    public static void main(String[] args) {
        InvoiceCalculator calculator = new InvoiceCalculator();
        calculator.addLine(10.0, 2).addLine(5.5, 1);
        System.out.println(calculator.computeTotal() + " " + calculator);
    }
}
