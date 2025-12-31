#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <map>

using namespace std;

constexpr int NV = 15;
constexpr double PI = 3.14159265358979323846;
alignas(64) const long double TX[NV] = {0,0.125,0.0625,0.2,0.1,0.35,0.075,0.075,-0.075,-0.075,-0.35,-0.1,-0.2,-0.0625,-0.125};
alignas(64) const long double TY[NV] = {0.8,0.5,0.5,0.25,0.25,0,0,-0.2,-0.2,0,0,0.25,0.25,0.5,0.5};

struct Poly {
    long double px[NV], py[NV];
    long double x0, y0, x1, y1;
};

inline void getPoly(long double cx, long double cy, long double deg, Poly& q) {
    long double rad = deg * (PI / 180.0L);
    long double s = sinl(rad), c = cosl(rad);
    long double minx = 1e9L, miny = 1e9L, maxx = -1e9L, maxy = -1e9L;
    for (int i = 0; i < NV; i++) {
        long double x = TX[i] * c - TY[i] * s + cx;
        long double y = TX[i] * s + TY[i] * c + cy;
        q.px[i] = x; q.py[i] = y;
        if (x < minx) minx = x; if (x > maxx) maxx = x;
        if (y < miny) miny = y; if (y > maxy) maxy = y;
    }
    q.x0 = minx; q.y0 = miny; q.x1 = maxx; q.y1 = maxy;
}

struct Cfg {
    int n;
    long double gx0, gy0, gx1, gy1;
    void add(long double x, long double y, long double a) {
        Poly p; getPoly(x, y, a, p);
        if (gx0 > p.x0) gx0 = p.x0;
        if (gx1 < p.x1) gx1 = p.x1;
        if (gy0 > p.y0) gy0 = p.y0;
        if (gy1 < p.y1) gy1 = p.y1;
    }
    long double side() { return max(gx1-gx0, gy1-gy0); }
};

int main(int argc, char** argv) {
    if (argc < 2) { cout << "Usage: ./verify <csv>" << endl; return 1; }
    ifstream f(argv[1]);
    string ln; getline(f, ln);
    map<int, Cfg> groups;
    while(getline(f, ln)) {
        size_t p1=ln.find(','), p2=ln.find(',',p1+1), p3=ln.find(',',p2+1);
        string id=ln.substr(0,p1), xs=ln.substr(p1+1,p2-p1-1), ys=ln.substr(p2+1,p3-p2-1), ds=ln.substr(p3+1);
        if(!xs.empty() && xs[0]=='s') xs=xs.substr(1);
        if(!ys.empty() && ys[0]=='s') ys=ys.substr(1);
        if(!ds.empty() && ds[0]=='s') ds=ds.substr(1);
        int n=stoi(id.substr(0,3));
        if (groups.find(n) == groups.end()) {
            groups[n].n = n;
            groups[n].gx0 = 1e9L; groups[n].gy0 = 1e9L;
            groups[n].gx1 = -1e9L; groups[n].gy1 = -1e9L;
        }
        groups[n].add(stold(xs), stold(ys), stold(ds));
    }
    
    long double totalObj = 0;
    for (auto& [n, c] : groups) {
        long double s = c.side();
        totalObj += s * s / n;
    }
    cout << fixed << setprecision(15) << totalObj << endl;
    return 0;
}
