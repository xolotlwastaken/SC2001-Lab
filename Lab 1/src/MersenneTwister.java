/**
 * Minimal MT19937 implementation with the same 32-bit output sequence as
 * std::mt19937 when seeded with one 32-bit value.
 */
public final class MersenneTwister {
    private static final int STATE_SIZE = 624;
    private static final int PERIOD_OFFSET = 397;
    private static final int MATRIX_A = 0x9908B0DF;
    private static final long UINT32_MODULUS = 1L << 32;

    private final int[] state = new int[STATE_SIZE];
    private int index = STATE_SIZE;

    public MersenneTwister(long seed) {
        state[0] = (int) seed;
        for (int i = 1; i < STATE_SIZE; i++) {
            long previous = Integer.toUnsignedLong(state[i - 1]);
            state[i] = (int) (1_812_433_253L
                    * (previous ^ (previous >>> 30))
                    + i);
        }
    }

    /**
     * Returns the next generator value as an unsigned 32-bit number stored in
     * a long.
     */
    public long nextUInt32() {
        if (index >= STATE_SIZE) {
            twist();
        }

        int value = state[index++];
        value ^= value >>> 11;
        value ^= (value << 7) & 0x9D2C5680;
        value ^= (value << 15) & 0xEFC60000;
        value ^= value >>> 18;
        return Integer.toUnsignedLong(value);
    }

    /**
     * Returns an unbiased value in [0, bound).
     */
    public int nextInt(int bound) {
        if (bound <= 0) {
            throw new IllegalArgumentException("bound must be positive");
        }
        long limit = UINT32_MODULUS / bound * bound;
        long value;
        do {
            value = nextUInt32();
        } while (value >= limit);
        return (int) (value % bound);
    }

    private void twist() {
        for (int i = 0; i < STATE_SIZE; i++) {
            int next = state[(i + 1) % STATE_SIZE];
            int upper = state[i] & 0x80000000;
            int lower = next & 0x7FFFFFFF;
            int combined = upper | lower;
            state[i] = state[(i + PERIOD_OFFSET) % STATE_SIZE]
                    ^ (combined >>> 1)
                    ^ ((combined & 1) == 1 ? MATRIX_A : 0);
        }
        index = 0;
    }
}
