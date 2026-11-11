MAX_SUPPLY = 21_000_000
INITIAL_REWARD = 50
HALVING_INTERVAL = 210_000

def block_reward(height):
    halvings = height // HALVING_INTERVAL

    if halvings >= 64:
        return 0

    return INITIAL_REWARD >> halvings

def remaining_supply(issued):
    return max(0, MAX_SUPPLY - issued)

if __name__ == "__main__":
    print("=== CUCO MINING REWARD ===")

    for height in [0, 1, 209999, 210000, 420000, 630000]:
        print(
            "Blok:", height,
            "| Reward:", block_reward(height), "CUCO"
        )

    print("Suplai maksimum:", MAX_SUPPLY)
