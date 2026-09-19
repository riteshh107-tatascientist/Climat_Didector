import { Routes, Route } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";

import Landing from "@/pages/Landing";
import Login from "@/pages/Login";
import Signup from "@/pages/Signup";
import Demo from "@/pages/Demo";
import Dashboard from "@/pages/Dashboard";
import RiskAnalysis from "@/pages/RiskAnalysis";
import Locations from "@/pages/Locations";
import History from "@/pages/History";
import Recommendations from "@/pages/Recommendations";
import Impact from "@/pages/Impact";
import Profile from "@/pages/Profile";
import NotFound from "@/pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/demo" element={<Demo />} />

      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="risk-analysis" element={<RiskAnalysis />} />
        <Route path="locations" element={<Locations />} />
        <Route path="history" element={<History />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="impact" element={<Impact />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
