# Sidebar for navigation
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Dashboard", "Data Upload", "Analysis", "Recommendations"]
    ["Dashboard", "Data Upload", "Analysis", "Urgent Alerts", "Recommendations"]
)
# Helper functions


title='Staffing Level vs Wait Time')
        st.plotly_chart(fig, use_container_width=True)
# PAGE 4: Recommendations
# PAGE 4: Urgent Alerts
elif page == "Urgent Alerts":
    st.header("🚨 Urgent Patient Alerts")
    
    if st.session_state.df is None:
        st.warning("Please upload data first!")
    else:
        df = st.session_state.df
        
        # Define urgent criteria
        st.subheader("Critical Conditions Detected")
        
        # Critical patients (triage level 1) with long wait times
        critical_long_wait = df[(df['triage_level'] == 1) & (df['wait_time_minutes'] > 15)]
        
        # Emergent patients (triage level 2) with very long wait times
        emergent_long_wait = df[(df['triage_level'] == 2) & (df['wait_time_minutes'] > 30)]
        
        # Any patient waiting more than 4 hours
        extreme_wait = df[df['wait_time_minutes'] > 240]
        
        # High volume periods with understaffing
        df['patients_per_staff'] = 1 / df['staff_count']  # Inverse ratio
        understaffed_periods = df[df['patients_per_staff'] > 0.2]  # More than 5 patients per staff
        
        # Display alerts
        alert_count = 0
        
        if len(critical_long_wait) > 0:
            alert_count += len(critical_long_wait)
            st.error(f"🔴 CRITICAL ALERT: {len(critical_long_wait)} Level 1 patients waiting over 15 minutes")
            
            # Show details
            with st.expander("View Critical Patients"):
                critical_display = critical_long_wait[['patient_id', 'wait_time_minutes', 'hour_of_day', 'staff_count']].copy()
                critical_display['urgency'] = 'IMMEDIATE'
                st.dataframe(critical_display, use_container_width=True)
        
        if len(emergent_long_wait) > 0:
            alert_count += len(emergent_long_wait)
            st.warning(f"🟠 HIGH ALERT: {len(emergent_long_wait)} Level 2 patients waiting over 30 minutes")
            
            with st.expander("View Emergent Patients"):
                emergent_display = emergent_long_wait[['patient_id', 'wait_time_minutes', 'hour_of_day', 'staff_count']].copy()
                emergent_display['urgency'] = 'HIGH'
                st.dataframe(emergent_display, use_container_width=True)
        
        if len(extreme_wait) > 0:
            alert_count += len(extreme_wait)
            st.error(f"🔴 EXTREME WAIT: {len(extreme_wait)} patients waiting over 4 hours")
            
            with st.expander("View Extreme Wait Patients"):
                extreme_display = extreme_wait[['patient_id', 'triage_level', 'wait_time_minutes', 'hour_of_day']].copy()
                extreme_display['urgency'] = 'EXTREME'
                st.dataframe(extreme_display, use_container_width=True)
        
        # Staffing alerts
        st.subheader("Staffing Alerts")
        
        # Find hours with potential understaffing
        hourly_load = df.groupby('hour_of_day').agg({
            'patient_id': 'count',
            'staff_count': 'mean',
            'wait_time_minutes': 'mean'
        }).round(1)
        
        hourly_load['patient_to_staff_ratio'] = hourly_load['patient_id'] / hourly_load['staff_count']
        high_load_hours = hourly_load[hourly_load['patient_to_staff_ratio'] > 3]  # More than 3 patients per staff
        
        if len(high_load_hours) > 0:
            st.warning(f"⚠️ STAFFING ALERT: {len(high_load_hours)} hours with high patient-to-staff ratio")
            
            with st.expander("View High Load Hours"):
                high_load_display = high_load_hours.copy()
                high_load_display.columns = ['Patients', 'Avg Staff', 'Avg Wait (min)', 'Ratio']
                st.dataframe(high_load_display, use_container_width=True)
        
        # Summary metrics
        st.subheader("Alert Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Alerts", alert_count)
        
        with col2:
            critical_count = len(critical_long_wait)
            st.metric("Critical Cases", critical_count, delta="Immediate action needed" if critical_count > 0 else None)
        
        with col3:
            avg_critical_wait = critical_long_wait['wait_time_minutes'].mean() if len(critical_long_wait) > 0 else 0
            st.metric("Avg Critical Wait", f"{avg_critical_wait:.1f} min" if avg_critical_wait > 0 else "0 min")
        
        with col4:
            understaffed_hours = len(high_load_hours)
            st.metric("Understaffed Hours", understaffed_hours)
        
        # Immediate actions needed
        if alert_count > 0:
            st.subheader("Immediate Actions Required")
            
            actions = []
            
            if len(critical_long_wait) > 0:
                actions.append("• **URGENT**: Immediately attend to Level 1 patients waiting over 15 minutes")
            
            if len(emergent_long_wait) > 0:
                actions.append("• **HIGH PRIORITY**: Address Level 2 patients waiting over 30 minutes")
            
            if len(extreme_wait) > 0:
                actions.append("• **ESCALATE**: Review cases with 4+ hour wait times immediately")
            
            if len(high_load_hours) > 0:
                peak_hour = high_load_hours['patient_to_staff_ratio'].idxmax()
                actions.append(f"• **STAFFING**: Add staff during hour {peak_hour}:00 (highest load)")
            
            for action in actions:
                st.markdown(action)
        else:
            st.success("✅ No urgent alerts detected. Current operations are within acceptable parameters.")
# PAGE 5: Recommendations
elif page == "Recommendations":
    st.header("💡 Recommendations")
    