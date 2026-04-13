const awsConfig = {
    Auth: {
        region: 'eu-west-2',
        userPoolId: 'eu-west-2_3El38gNPR',
        userPoolWebClientId: 'k6cp46tm2t63vnubqv6ecmj5i',
    },
    API: {
        endpoints: [
            {
                name: 'CrowdMonitorAPI',
                endpoint: 'https://ly7jsdllj4.execute-api.eu-west-2.amazonaws.com',
                region: 'eu-west-2' 
            }
        ]
    }
}


export default awsConfig;
