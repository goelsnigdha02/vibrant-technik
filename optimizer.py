import math

CARRIER_MAX_GAP = 1000
CARRIER_END_GAP = 150
CARRIER_LENGTH = 3000

def calculate_divisions(width, height, pitch, orientation):

    divisions = math.ceil(height / pitch)

    # if orientation == 'Vertical':
    #     temp = width
    #     width = height
    #     height = temp

    return divisions


def filter_inv(df, product):#, divisions):
    inv = df[(df['name'] == product)]# & (df['stock'] >= divisions)]
    return inv


def find_counts(df):
    counts = {}
    for _, row in df.iterrows():
        if int(row['length']) not in counts:
            counts[row['length']] = 0
        counts[row['length']] += row['stock']
    
    return counts


def find_combinations(target, lengths, counts, req_pieces, wastage):
    output = set()
    
    def dfs(total, arr, i):
        if target <= total <= target + wastage:
            stock_avail = True
            for l in set(arr):
                req = arr.count(l) * req_pieces
                if counts[l] < req:
                    stock_avail = False
                    break
            if stock_avail:
                output.add(tuple(sorted(arr)))
            return
        
        if (total > target + wastage) or (i >= len(lengths)):
            return
        
        arr.append(lengths[i])
        dfs(total + lengths[i], arr, i)
        arr.pop()
        dfs(total, arr, i + 1)
    
    dfs(0, [], 0)
    return [list(x) for x in output]


def carrier_calculation(
    length_combination,
    carrier_lengths,
    no_carriers_per_piece
):
    centre_gaps_per_piece = []

    for l in length_combination:
        carrier_lengths = 1 # for end piece
        centre_width = l - (2 * CARRIER_END_GAP)
        if centre_width >= 900:
            carrier_lengths += math.ceil(centre_width / CARRIER_MAX_GAP)
            centre_gap = centre_width / (carrier_lengths - 1)
        else:
            carrier_lengths += 1
            centre_gap = centre_width

        centre_gaps_per_piece.append(centre_gap)
        no_carriers_per_piece.append(carrier_lengths)

    return centre_gaps_per_piece, no_carriers_per_piece


def calculate_carrier_distances(centre_gaps_per_piece,
                                no_carriers_per_piece
                                ):
    carrier_distances = []
    
    for j in range(len(no_carriers_per_piece)):
        curr = 0
        curr_distances = []
        for i in range(no_carriers_per_piece[j]):
            if i == 0:
                curr += CARRIER_END_GAP
            else:
                curr += centre_gaps_per_piece[j]
            curr_distances.append(curr)
        carrier_distances.append(curr_distances)

    return carrier_distances