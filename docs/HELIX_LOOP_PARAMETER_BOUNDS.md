# Właściwości i granice parametrów helisy oraz trójpętli

**Data:** 2026-11-08  
**Status:** audyt źródeł GIA-TIMDR + wnioski matematyczne; nie jest to walidacja fizyczna ani opis potwierdzonej dynamiki produkcyjnego Helix-Lock.

## 1. Najważniejsze rozróżnienie

W repozytoriach występują co najmniej cztery różne obiekty, których nie wolno utożsamiać:

1. **Helisa geometryczna** — krzywa 3D opisana promieniem i skokiem; ma krzywiznę κ i torsję Freneta-Serreta τ.
2. **Trójwęzeł (trefoil)** — zamknięta krzywa węzłowa, nie zwykła helisa o stałej κ i τ na całej długości.
3. **Trójpętlowy model Möbiusa** — propozycja dynamiki trzech amplitud i warunku holonomii/sklejenia.
4. **Chronoproces TIMDR** — aktualnie kontener wspólnego nośnika T i trzech niezależnych projekcji M/S, G, K; nie jest sam w sobie sprzężonym regulatorem trzech oscylatorów.

Dokument `docs/geometry/tourosomobius.md` nazywa warstwy Λ–τ–ρ, ale sam opisuje je jako formalny model koncepcyjny. Podane tam 45°, 60° i 1/2 nie mają wyprowadzonych zakresów dopuszczalności ani walidacji numerycznej. Nie należy traktować ich jako potwierdzonych progów stabilności.

## 2. Ograniczenia czystej helisy

Dla standardowej helisy

`r(t) = (a cos t, a sin t, h t)`,

gdzie `a > 0` jest promieniem, a `2πh` skokiem na pełen obrót, zachodzi:

- `κ = a / (a² + h²)` — krzywizna;
- `τ = h / (a² + h²)` — torsja Freneta-Serreta;
- `τ/κ = h/a` — stosunek torsji do krzywizny;
- `sqrt(κ² + τ²) = 1/sqrt(a²+h²)` — wspólna skala krzywizny i torsji.

Konsekwencje:
- κ i τ nie są niezależnymi pokrętłami: ich stosunek ustala kąt/skok helisy, a ich wspólna skala ustala rozmiar helisy.
- Przy ustalonym promieniu `a`, `κ` nie przekracza `1/a` (granica przy `h=0`, czyli okręgu); dla rosnącego |h| krzywizna maleje.
- Znak τ rozróżnia prawoskrętność/lewoskrętność, ale model G-Rezonans używa `|τ|`, więc obecna macierz sprzężeń traci informację o chiralności.
- Nie istnieje uniwersalny limit liczbowy κ lub τ bez ustalenia skali długości, promienia, skoku i jednostek konkretnego układu.

Źródła geometrii standardowej: do Carmo, *Differential Geometry of Curves and Surfaces*; przegląd równań helisy: https://link.springer.com/article/10.1007/s00214-009-0639-4.

## 3. Co wynika z istniejącego trójwęzła GIA-TIMDR

Źródło: `jbackk-lang/GIA-TIMDR/docs/geometry/TIMDR_Trefoil_FrenetTorsion.md` oraz `core/trefoil_frenet_torsion.py`.

- Badana krzywa jest konkretnym trefoilem: `x=sin(t)+2sin(2t)`, `y=cos(t)-2cos(2t)`, `z=-sin(3t)`.
- Dla idealnego trójwęzła dokument raportuje w trzech symetrycznych węzłach `κ≈0.2062`, `τ≈0.3509`.
- Są to wartości tego konkretnego parametryzowanego modelu i próbkowania, a nie uniwersalne granice każdej helisy lub pętli.
- Torsja jest bramkowana, gdy `κ < 1e-4`; prędkość jest bramkowana poniżej `1e-6`. To progi numerycznej ochrony estymatora różnic skończonych przed niestabilnością, nie granice fizycznej samoregulacji.
- Na realnych, krótkich/szorstkich szeregach wielokrotne różniczkowanie wzmacnia szum; dokument odnotowuje nieudaną próbę na krótkich danych pogodowych.

## 4. Granice istniejącego operatora G-Rezonans (G5)

Źródła: `jbackk-lang/GIA-TIMDR/core/geometric_resonance_operator.py`, `docs/geometry/TIMDR_GResonance_Operator.md`.

Model buduje pierścień N sprzężonych oscylatorów:

`M x'' + Γ x' + K x = F(t)`

z `N >= 3`, masami `m_i`, tłumieniem `γ`, sztywnością własną proporcjonalną do `κ_i` i sprzężeniami sąsiednimi proporcjonalnymi do `|τ_i|`.

Jawne warunki dopuszczalności obecnego predykatu stabilności:
- `M` symetryczna dodatnio określona (w praktyce każda masa > 0);
- `K` symetryczna dodatnio określona;
- `Γ` symetryczna dodatnio określona (tłumienie > 0 na każdym węźle);
- `N >= 3` i długości wektorów κ, τ, m zgodne z N.

Przy dodatnich `k_scale`, `kc_scale`, `κ_i > 0`, `|τ_i| >= 0` i `m_i > 0`, macierz `K` ma postać dodatniej diagonalnej części plus ważony laplasjan pierścienia, więc jest dodatnio określona. W tej konkretnej konstrukcji nie ma górnego limitu |τ| wyprowadzonego z warunku dodatniej określoności: większe |τ| wzmacnia sprzężenie i przesuwa widmo. To nie znaczy, że dowolnie duże |τ| jest fizycznie sensowne — `k_scale`, `kc_scale` i `γ` nie są skalibrowane na realnym obiekcie.

Jeżeli krzywizna węzła może być ujemna, dodatnia określoność K zależy od całego widma macierzy, a nie od jednego prostego limitu κ_i. Trzeba sprawdzić najmniejszą wartość własną K po każdej zmianie geometrii.

**Istotna luka:** `|τ|` oznacza, że obecny operator nie rozróżnia znaku torsji/chiralności. Jeżeli kierunek helisy ma wpływać na kierunek przepływu informacji, obecna macierz tego nie koduje.

## 5. Granica parametru Λ w zaproponowanym operatorze trzech kanałów

Źródła: `jbackk-lang/GIA-TIMDR/docs/theory/Three_Loop_Mobius_Information_Dynamics.md` oraz `Three_Loop_Mobius_Spectral_And_Bundle_Extension.md`.

Dla `J(Λ)=P−ΛP²`, `P³=I`, rzeczywistego Λ i nieznormalizowanej iteracji `Ψ[n+1]=JΨ[n]`:

`ρ(J)=max(|1−Λ|, sqrt(1+Λ+Λ²))`.

Z analizy widma:
- dla `Λ=0`: `ρ(J)=1` — cykliczna permutacja jest normozachowująca;
- dla każdego rzeczywistego `Λ != 0`: `ρ(J)>1` — istnieje mod, którego amplituda rośnie;
- nie istnieje rzeczywisty Λ, dla którego oryginalne J jest ścisłą kontrakcją.

Zatem jeśli ten operator miałby być użyty jako samodzielny krok ewolucji, **nie wolno interpretować Λ jako bezpiecznego, nieograniczonego parametru sprzężenia**. Potrzebna jest jawna normalizacja/tłumienie, np. `A=e^(−γ)J/ρ(J)` z `γ>=0`, albo inna dynamika o udowodnionym ograniczeniu normy. To jest warunek matematyczny tego kandydującego operatora, nie potwierdzony mechanizm produkcyjnego Helix.

## 6. Co mówią obecne testy o czasie i pełnym obiegu

Źródła: `experiments/chronoprocess_triple_loop_duration_sweep.py`, `chronoprocess_triple_loop_time_history.py`, `chronoprocess_coupled_phase_recovery.py`, `triple_loop_transition_probe.py` w GIA-TIMDR.

- `P³=I` daje domknięcie permutacji kanałów po trzech obiegach; nie usuwa zaburzenia stanu.
- Wspólne odstrojenie wszystkich trzech zegarów zachowuje relacje względne. To common-mode control, nie samonaprawa.
- Różnicowe odstrojenie pozostawia ślad w skumulowanej fazie nawet po powrocie chwilowej częstotliwości do nominalnej.
- Dodatnie sprzężenie Kuramoto w modelu kandydującym może przywrócić koherencję dla części scenariuszy; prawo to jest dopisane eksperymentalnie i nie należy do aktualnego Chronoprocesu.
- Istniejący sweep używa `K={0,0.2,0.4,0.8,1.6}`, czasów impulsu `0.1–4.0 s`, amplitudy `1.2 rad/s` i kryterium `R>=0.99` utrzymanego przez 0.5 s. To zakres testu, nie uniwersalna granica helisy.

## 7. Wnioski dla hipotezy użytkownika

Najbardziej obiecujący kierunek to nie szukanie jednej maksymalnej wartości „skrętu”, lecz granicy dopuszczalnego stanu w przestrzeni parametrów:

`(κ_i, τ_i, N, Λ, γ, K_c, Δω, T_cycle, duration, noise)`.

Proponuję rozdzielić trzy powierzchnie graniczne:
1. **Geometryczna:** czy krzywa/pierścień pozostaje regularny, nie samoprzecinający się w zadanej skali i poprawnie próbkowany.
2. **Dynamiczna:** czy macierze układu pozostają dodatnio określone / czy spełniony jest warunek synchronizacji dla przyjętego prawa ruchu.
3. **Informacyjna:** czy po pełnym cyklu poprawnie dekodowane są relacje/payload, a nie tylko czy R lub błąd fazowy wrócił do progu.

Kluczowy eksperyment następny: wykonać mapę `amplituda × czas impulsu × asymetria pętli × sprzężenie`, z osobnym pomiarem κ, τ, holonomii, fazy względnej, koherencji i dokładności payloadu. Dodać test znaku τ (lustrzane odbicie/chiralność), nierówne częstotliwości własne oraz legalną zmianę payloadu w trakcie cyklu. Ustalić progi przed uruchomieniem holdoutu.

## 8. Granice obecnej wiedzy

- „Potrójny Tourosomobius” jest w źródle koncepcyjną notacją; warunek Borromejski i liczby 45°/60°/1/2 nie mają tam kompletnego dowodu ani walidacji.
- Standardowa helisa ma stałe κ i τ; trefoil ma zmienne κ(s), τ(s) i jest innym obiektem.
- Aktualny Chronoproces jest orkiestratorem projekcji, nie implementacją samoregulującej trójhelisy.
- Żaden z opisanych eksperymentów nie dowodzi odzyskiwania informacji w oryginalnym TIMDR ani w produkcyjnym Helix-Lock.
- Stałe mechaniczne G5 i zakresy sprzężenia wymagają kalibracji na danych/układzie fizycznym, jeśli model ma mieć interpretację fizyczną.

## Źródła repozytoryjne

- GIA-TIMDR `docs/geometry/tourosomobius.md`
- GIA-TIMDR `docs/geometry/TIMDR_Trefoil_FrenetTorsion.md`
- GIA-TIMDR `docs/geometry/TIMDR_GResonance_Operator.md`
- GIA-TIMDR `docs/theory/Three_Loop_Mobius_Information_Dynamics.md`
- GIA-TIMDR `docs/theory/Three_Loop_Mobius_Spectral_And_Bundle_Extension.md`
- GIA-TIMDR `docs/theory/TIMDR_Chronoprocess.md`
- GIA-TIMDR `experiments/chronoprocess_triple_loop_duration_sweep.py`
- GIA-TIMDR `experiments/chronoprocess_coupled_phase_recovery.py`
