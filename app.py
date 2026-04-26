import streamlit as st
import lightkurve as lk
import matplotlib.pyplot as plt

st.set_page_config(page_title="Exoplanet Transit Finder", layout="wide")
st.title("Exoplanet Transit Finder (NASA TESS)")

# --- Sidebar ---
mode = st.sidebar.radio(
    "Download mode",
    ["Fast mode (3 sectors, ~1-2 min)", "Full mode (all sectors, ~10-20 min)"],
)
fast_mode = mode.startswith("Fast")
if not fast_mode:
    st.sidebar.warning(
        "Full mode may take 10–20 minutes depending on how many sectors are available."
    )

# --- Cached helpers ---
@st.cache_data(show_spinner=False)
def search_tess(star_name):
    return lk.search_lightcurve(star_name, mission="TESS", author="SPOC")

def download_and_stitch(star_name, fast_mode):
    result = lk.search_lightcurve(star_name, mission="TESS", author="SPOC")
    to_download = result[-3:] if fast_mode else result
    collection = to_download.download_all()
    if collection is None or len(collection) == 0:
        raise ValueError("Download returned no data.")
    normalized = lk.LightCurveCollection(
        [lc.remove_nans().normalize() for lc in collection]
    )
    stitched = normalized.stitch()
    return stitched.remove_outliers(sigma=4)

# --- Main UI ---
star_name = st.text_input("Enter a star name (e.g. TOI-700, Kepler-10, TIC 261136679):")

if st.button("Search for Transits") and star_name.strip():
    with st.spinner(f"Checking TESS database for '{star_name}'..."):
        try:
            search_result = search_tess(star_name)
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.stop()

    if len(search_result) == 0:
        st.error(
            f"'{star_name}' was not found in the TESS SPOC database. "
            "Check the spelling or try a TIC ID (e.g. TIC 261136679)."
        )
        st.stop()

    n_sectors = min(3, len(search_result)) if fast_mode else len(search_result)
    st.info(
        f"Found {len(search_result)} sector(s) for '{star_name}'. "
        f"Downloading {n_sectors} sector(s)..."
    )

    spinner_msg = (
        "Downloading light curves..."
        if fast_mode
        else "Downloading all light curves (this may take a while)..."
    )
    with st.spinner(spinner_msg):
        try:
            lc = download_and_stitch(star_name, fast_mode)
        except Exception as e:
            st.error(f"Failed to download data: {e}")
            st.stop()

    # --- Raw light curve ---
    st.subheader("Raw Light Curve")
    fig_lc, ax_lc = plt.subplots(figsize=(12, 3))
    ax_lc.scatter(lc.time.value, lc.flux.value, s=0.5, c="steelblue", alpha=0.6)
    ax_lc.set_xlabel("Time (BTJD)")
    ax_lc.set_ylabel("Normalized Flux")
    ax_lc.set_title(f"{star_name} — TESS Light Curve")
    st.pyplot(fig_lc)
    plt.close(fig_lc)

    # --- BLS periodogram ---
    with st.spinner("Running BLS periodogram..."):
        try:
            period_min = 0.5
            period_max = min(27.0, (lc.time.value[-1] - lc.time.value[0]) / 2)
            bls = lc.to_periodogram(
                method="bls",
                minimum_period=period_min,
                maximum_period=period_max,
                frequency_factor=50,
            )
        except Exception as e:
            st.error(f"BLS periodogram failed: {e}")
            st.stop()

    best_period = bls.period_at_max_power.value
    best_power = bls.max_power.value
    best_depth = float(bls.compute_stats(
        bls.period_at_max_power,
        bls.duration_at_max_power,
        bls.transit_time_at_max_power,
    )["depth"][0])

    st.subheader("BLS Periodogram")
    fig_bls, ax_bls = plt.subplots(figsize=(12, 3))
    ax_bls.plot(bls.period.value, bls.power.value, lw=0.7, c="darkorange")
    ax_bls.axvline(best_period, color="red", ls="--", lw=1.2,
                   label=f"Best period: {best_period:.4f} d")
    ax_bls.set_xlabel("Period (days)")
    ax_bls.set_ylabel("BLS Power")
    ax_bls.set_title(f"{star_name} — BLS Periodogram")
    ax_bls.legend()
    st.pyplot(fig_bls)
    plt.close(fig_bls)

    col1, col2, col3 = st.columns(3)
    col1.metric("Best Period (days)", f"{best_period:.4f}")
    col2.metric("Peak BLS Power", f"{best_power:.2f}")
    col3.metric("Transit Depth", f"{best_depth:.5f}")

    # --- Significance check & phase-folded plot ---
    POWER_THRESHOLD = 50
    DEPTH_THRESHOLD = 0.0005

    significant = best_power >= POWER_THRESHOLD and best_depth >= DEPTH_THRESHOLD

    st.subheader("Phase-Folded Transit")
    if not significant:
        st.warning(
            f"No significant transit detected. "
            f"Peak power ({best_power:.2f}) must be ≥ {POWER_THRESHOLD} "
            f"and depth ({best_depth:.5f}) must be ≥ {DEPTH_THRESHOLD}."
        )
    else:
        t0 = bls.transit_time_at_max_power.value
        folded = lc.fold(period=best_period, epoch_time=t0)
        binned = folded.bin(bins=100)

        fig_fold, ax_fold = plt.subplots(figsize=(10, 4))
        ax_fold.scatter(folded.time.value, folded.flux.value,
                        s=0.5, c="steelblue", alpha=0.3, label="Data")
        ax_fold.plot(binned.time.value, binned.flux.value,
                     "r-", lw=2, label="Binned")
        ax_fold.set_xlabel("Phase (days)")
        ax_fold.set_ylabel("Normalized Flux")
        ax_fold.set_title(
            f"{star_name} — Phase-folded at P = {best_period:.4f} d"
        )
        ax_fold.legend()
        st.pyplot(fig_fold)
        plt.close(fig_fold)

        st.success(
            f"Transit candidate detected! Period = {best_period:.4f} d, "
            f"depth ≈ {best_depth:.5f}, BLS power = {best_power:.2f}."
        )
