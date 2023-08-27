def addn(d, k, n):
    if k in d:
        d[k] = d[k] + n
    else:
        d[k] = n

def get_ave(d):
    total = 0
    num = 0
    for k in d:
        total = total + (k * d[k])
        num = num + d[k]
    return float(total) / float(num)

def get_stats(event, days):
    up = []
    for d in range(len(event['div_size'][0])):
        up.append({})
    upa = {}

    for day_num in range(event['days']):
        if day_num == len(days):
            days.append({})
        m = event['move'][day_num]
        div_num = -1
        div_foot = 0
        dstat = None
        for crew_num in range(len(m)):
            if crew_num == div_foot:
                div_num += 1

                # if crews have withdrawn then we can go off the bottom
                if div_num >= len(event['div_size'][day_num]):
                    break

                dstat = up[div_num]
                div_foot += event['div_size'][day_num][div_num]
                
            s = m[crew_num]
            if s is not None:
                if s < 0:
                    s = -s
                addn(days[day_num], s, 1)
                addn(dstat, s, 1)
                addn(upa, s, 1)

    for d in range(len(up)):
        print("%s/%s/%s %d %g %s" % (event['short'], event['year'], event['gender'], d+1, get_ave(up[d]), up[d]))

    print("%s/%s/%s %g %s" % (event['short'], event['year'], event['gender'], get_ave(upa), upa))

def output_days(days):
    day_num = 1
    for d in days:
        print("Day %d %g %s" % (day_num, get_ave(d), d))
        day_num += 1
