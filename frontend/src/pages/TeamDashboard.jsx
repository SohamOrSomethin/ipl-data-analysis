import React, {useEffect, useState} from "react";
import { useParams } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const TeamDashboard = () => {
    const {teamName} = useParams();
    const [teamData, setTeamData] = useState(null);

    useEffect(() => {
        fetch(`http://localhost:5000/api/teams/${teamName}/summary`)
            .then(res => res.json())
            .then(data => setTeamData(data));
    }, [teamName]);

    return (
        <div>
            <h1>{teamName}</h1>
        </div>
    );
}

export default TeamDashboard;